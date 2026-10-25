<template>
  <div class="upload-view">
    <el-card class="upload-card">
      <template #header>
        <span>上传数据</span>
      </template>
      <el-form :inline="true">
        <el-form-item label="数据类型">
          <el-radio-group v-model="dataType">
            <el-radio-button value="table">结构化表格</el-radio-button>
            <el-radio-button value="doc">文本文档</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="description" placeholder="选填" style="width: 200px" />
        </el-form-item>
      </el-form>
      <el-upload
        drag
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFile"
        accept=".csv,.xlsx,.xls,.txt,.md,.pdf,.docx"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或 <em>点击选择文件</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            {{ dataType === 'table' ? '支持 CSV / Excel 表格' : '支持 txt / md / pdf / docx 文档' }}
          </div>
        </template>
      </el-upload>
    </el-card>

    <el-card class="list-card">
      <template #header>
        <span>已上传数据集</span>
      </template>
      <el-table :data="datasets" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="名称" />
        <el-table-column label="类型" width="110">
          <template #default="{ row }">
            <el-tag :type="row.type === 'table' ? 'primary' : 'success'">
              {{ row.type === 'table' ? '表格' : '文档' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="备注" />
        <el-table-column label="规模" width="120">
          <template #default="{ row }">
            <span v-if="row.type === 'table'">{{ schemaLen(row) }} 列</span>
            <span v-else>{{ row.chunk_count }} 段</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { fetchDatasets, uploadFile } from '../api'

const dataType = ref('table')
const description = ref('')
const datasets = ref([])
const loading = ref(false)

function schemaLen(row) {
  return Array.isArray(row.schema_json) ? row.schema_json.length : 0
}

async function load() {
  loading.value = true
  try {
    datasets.value = await fetchDatasets()
  } finally {
    loading.value = false
  }
}

async function handleFile(file) {
  try {
    const res = await uploadFile(file.raw, dataType.value, description.value)
    ElMessage.success(res.data.message || '上传成功')
    description.value = ''
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  }
}

onMounted(load)
</script>

<style scoped>
.upload-view { padding: 24px; overflow: auto; height: 100%; }
.upload-card { margin-bottom: 20px; }
.list-card { }
</style>
