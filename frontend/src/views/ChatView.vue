<template>
  <div class="chat-view">
    <div class="chat-head">与智能数据 Agent 对话（基于数据库数据 + 文档分析回答）</div>
    <div class="chat-body" ref="bodyRef">
      <div v-if="messages.length === 0" class="empty">
        请先在上传要分析的数据，然后在此提问，例如：<br />
        「哪个地区销售额最高？」「各月销售额的走势如何？」
      </div>
      <div
        v-for="(m, idx) in messages"
        :key="idx"
        class="msg"
        :class="m.role"
      >
        <div class="avatar">{{ m.role === 'user' ? '我' : 'A' }}</div>
        <div class="bubble">
          <!-- assistant structured result -->
          <template v-if="m.role === 'assistant' && m.extra">
            <div v-if="m.extra.sql" class="sql-block">
              <div class="sql-label">执行的 SQL：</div>
              <code>{{ m.extra.sql }}</code>
            </div>
            <div v-if="m.extra.table && m.extra.table.rows && m.extra.table.rows.length" class="block">
              <div class="block-label">数据结果</div>
              <DataTable :columns="m.extra.table.columns" :rows="m.extra.table.rows" />
            </div>
            <div v-if="m.extra.chart" class="block">
              <div class="block-label">可视化</div>
              <DataChart :chart="m.extra.chart" />
            </div>
            <div v-if="m.extra.docs && m.extra.docs.length" class="block">
              <div class="block-label">参考文档片段</div>
              <div class="doc-item" v-for="(d, i) in m.extra.docs" :key="i">· {{ d.content }}</div>
            </div>
          </template>
          <!-- text -->
          <div v-if="m.content" class="text" v-html="renderMD(m.content)"></div>
          <div v-if="m.streaming && !m.content" class="typing">思考中…</div>
        </div>
      </div>
    </div>
    <div class="chat-input">
      <el-input
        v-model="input"
        type="textarea"
        :rows="2"
        placeholder="输入你的问题，Enter 发送，Shift+Enter 换行"
        :disabled="sending"
        @keydown.enter.exact.prevent="send"
      />
      <el-button type="primary" :loading="sending" @click="send" class="send-btn">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import DataTable from '../components/DataTable.vue'
import DataChart from '../components/DataChart.vue'

const messages = ref([])
const input = ref('')
const sending = ref(false)
const bodyRef = ref(null)

function renderMD(text) {
  let t = String(text)
  t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  t = t.replace(/`(.+?)`/g, '<code>$1</code>')
  t = t.replace(/\n/g, '<br/>')
  return t
}

function scrollToBottom() {
  nextTick(() => {
    if (bodyRef.value) bodyRef.value.scrollTop = bodyRef.value.scrollHeight
  })
}

async function send() {
  const text = input.value.trim()
  if (!text || sending.value) return
  input.value = ''
  sending.value = true
  messages.value.push({ role: 'user', content: text })
  const assistant = { role: 'assistant', content: '', extra: null, streaming: true }
  messages.value.push(assistant)
  scrollToBottom()

  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('da_token') || ''}`,
      },
      body: JSON.stringify({ message: text, history: [] }),
    })
    if (!resp.ok) throw new Error('请求失败')
    const reader = resp.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      let idx
      while ((idx = buffer.indexOf('\n')) >= 0) {
        const line = buffer.slice(0, idx).trim()
        buffer = buffer.slice(idx + 1)
        if (line.startsWith('data: ')) {
          const payload = JSON.parse(line.slice(6))
          if (payload.type === 'meta') {
            assistant.extra = payload.extra
          } else if (payload.type === 'delta') {
            assistant.content += payload.text
            scrollToBottom()
          } else if (payload.type === 'done') {
            assistant.streaming = false
          }
        }
      }
    }
  } catch (e) {
    assistant.content = '（请求失败，请检查后端服务）'
    ElMessage.error('聊天请求失败')
  } finally {
    assistant.streaming = false
    sending.value = false
    scrollToBottom()
  }
}

onMounted(scrollToBottom)
</script>

<style scoped>
.chat-view { display: flex; flex-direction: column; height: 100%; }
.chat-head {
  height: 56px; line-height: 56px; padding: 0 24px; background: #fff;
  border-bottom: 1px solid #e6e6e6; font-weight: 600; color: #333;
}
.chat-body { flex: 1; overflow-y: auto; padding: 20px 24px; background: #f7f8fa; }
.empty { text-align: center; color: #999; margin-top: 60px; line-height: 1.8; }
.msg { display: flex; margin-bottom: 18px; }
.msg.user { flex-direction: row-reverse; }
.avatar {
  width: 36px; height: 36px; border-radius: 50%; flex: none;
  color: #fff; text-align: center; line-height: 36px; font-size: 14px;
  background: #909399;
}
.msg.user .avatar { background: #409eff; }
.bubble {
  max-width: 70%; margin: 0 12px; padding: 12px 16px; border-radius: 8px;
  background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,.08); overflow: hidden;
}
.msg.user .bubble { background: #d9ecff; }
.text { line-height: 1.7; word-break: break-word; }
.typing { color: #999; }
.block { margin-top: 12px; }
.block-label { font-size: 13px; font-weight: 600; color: #606266; margin-bottom: 8px; }
.sql-block { margin-bottom: 10px; }
.sql-label { font-size: 13px; font-weight: 600; color: #67c23a; }
.sql-block code {
  display: block; background: #f4f4f5; padding: 8px 10px; border-radius: 4px;
  margin-top: 4px; font-size: 12px; word-break: break-all;
}
.doc-item { font-size: 13px; color: #606266; margin-bottom: 4px; }
.chat-input {
  display: flex; gap: 12px; padding: 16px 24px; background: #fff;
  border-top: 1px solid #e6e6e6;
}
.chat-input .el-textarea { flex: 1; }
.send-btn { height: auto; }
</style>
