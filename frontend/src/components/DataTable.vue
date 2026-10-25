<template>
  <div class="data-table">
    <el-table :data="rows" size="small" border max-height="300">
      <el-table-column
        v-for="(col, i) in columns"
        :key="col"
        :prop="String(i)"
        :label="col"
      />
    </el-table>
  </div>
</template>

<script setup>
const props = defineProps({
  columns: { type: Array, default: () => [] },
  rows: { type: Array, default: () => [] },
})
</script>
