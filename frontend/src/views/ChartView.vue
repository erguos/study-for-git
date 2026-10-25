<template>
  <div class="chart-view">
    <el-card class="selector-card">
      <template #header>
        <span>图表可视化</span>
      </template>
      <el-form :inline="true">
        <el-form-item label="选择数据集">
          <el-select v-model="selectedDataset" placeholder="请选择表格数据集" @change="onDatasetChange" filterable>
            <el-option v-for="d in tableDatasets" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="图表类型">
          <el-select v-model="chartType">
            <el-option label="柱状图" value="bar" />
            <el-option label="折线图" value="line" />
            <el-option label="饼图" value="pie" />
          </el-select>
        </el-form-item>
        <el-form-item label="X轴字段">
          <el-select v-model="xField" placeholder="选择字段" :disabled="!selectedDataset">
            <el-option v-for="c in columns" :key="c.name" :label="c.name" :value="c.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="Y轴字段">
          <el-select v-model="yField" placeholder="选择字段" :disabled="!selectedDataset">
            <el-option v-for="c in numericColumns" :key="c.name" :label="c.name" :value="c.name" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="renderChart" :disabled="!selectedDataset || !xField || !yField">
            生成图表
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="chart-card" v-if="chartData">
      <template #header>
        <span>{{ selectedDatasetName }} - {{ chartTypeLabel }}</span>
      </template>
      <div ref="chartRef" class="chart-container"></div>
    </el-card>

    <el-empty v-if="!selectedDataset" description="请先选择一个数据集" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { fetchDatasets } from '../api'

const tableDatasets = ref([])
const selectedDataset = ref(null)
const selectedDatasetName = ref('')
const chartType = ref('bar')
const xField = ref('')
const yField = ref('')
const columns = ref([])
const numericColumns = ref([])
const chartData = ref(null)
const chartRef = ref(null)
let chartInstance = null

const chartTypeLabel = computed(() => {
  const map = { bar: '柱状图', line: '折线图', pie: '饼图' }
  return map[chartType.value] || '图表'
})

async function loadDatasets() {
  try {
    const list = await fetchDatasets()
    tableDatasets.value = list.filter(d => d.type === 'table' && d.status === 'ready')
  } catch (e) {
    ElMessage.error('加载数据集失败')
  }
}

async function onDatasetChange() {
  const ds = tableDatasets.value.find(d => d.id === selectedDataset.value)
  if (!ds) return
  selectedDatasetName.value = ds.name
  columns.value = ds.schema_json || []
  numericColumns.value = columns.value.filter(c => 
    c.type && c.type.toUpperCase().match(/INT|BIGINT|FLOAT|DOUBLE|DECIMAL/)
  )
  xField.value = ''
  yField.value = ''
  chartData.value = null
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
}

async function renderChart() {
  if (!selectedDataset.value || !xField.value || !yField.value) return
  try {
    const resp = await fetch(`/api/datasets/${selectedDataset.value}/data`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('da_token') || ''}` }
    })
    if (!resp.ok) throw new Error()
    const data = await resp.json()
    const rows = data.rows || []
    const xIdx = columns.value.findIndex(c => c.name === xField.value)
    const yIdx = columns.value.findIndex(c => c.name === yField.value)
    if (xIdx < 0 || yIdx < 0) return
    chartData.value = {
      x: rows.map(r => r[xIdx]),
      y: rows.map(r => parseFloat(r[yIdx]) || 0)
    }
    await nextTick()
    drawChart()
  } catch (e) {
    ElMessage.error('获取数据失败')
  }
}

function drawChart() {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)
  const option = buildOption()
  chartInstance.setOption(option, true)
}

function buildOption() {
  const type = chartType.value
  const xData = chartData.value.x
  const yData = chartData.value.y
  if (type === 'pie') {
    return {
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '60%',
        data: xData.map((name, i) => ({ name: String(name), value: yData[i] }))
      }]
    }
  }
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 20, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: xData, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value' },
    series: [{
      type: type === 'line' ? 'line' : 'bar',
      data: yData,
      smooth: true,
      itemStyle: { color: '#409eff' }
    }]
  }
}

onMounted(() => {
  loadDatasets()
  window.addEventListener('resize', () => chartInstance && chartInstance.resize())
})

onBeforeUnmount(() => {
  if (chartInstance) chartInstance.dispose()
  window.removeEventListener('resize', () => chartInstance && chartInstance.resize())
})
</script>

<style scoped>
.chart-view { padding: 24px; overflow: auto; height: 100%; }
.selector-card { margin-bottom: 20px; }
.chart-card { min-height: 400px; }
.chart-container { width: 100%; height: 350px; }
</style>