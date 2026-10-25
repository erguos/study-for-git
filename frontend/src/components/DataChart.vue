<template>
  <div ref="el" class="data-chart"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  chart: { type: Object, required: true },
})

const el = ref(null)
let instance = null

function buildOption(c) {
  const xData = c.data.map((r, i) => (i === 0 && c.x_field != null ? r[0] : r[0]))
  const x = c.data.map((r) => r[0])
  const y = c.data.map((r) => r[1])
  if (c.type === 'pie') {
    return {
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '60%',
        data: x.map((name, i) => ({ name: String(name), value: y[i] })),
      }],
    }
  }
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 20, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: x, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value' },
    series: [{
      type: c.type === 'line' ? 'line' : 'bar',
      data: y,
      smooth: true,
      itemStyle: { color: '#409eff' },
    }],
  }
}

function render() {
  if (!instance && el.value) {
    instance = echarts.init(el.value)
  }
  if (instance) {
    instance.setOption(buildOption(props.chart), true)
  }
}

onMounted(() => {
  render()
  window.addEventListener('resize', () => instance && instance.resize())
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', () => instance && instance.resize())
  if (instance) {
    instance.dispose()
    instance = null
  }
})

watch(() => props.chart, () => render(), { deep: true })
</script>

<style scoped>
.data-chart { width: 100%; height: 300px; }
</style>
