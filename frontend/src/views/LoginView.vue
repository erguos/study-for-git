<template>
  <div class="login-view">
    <!-- 动态背景光斑 -->
    <div class="bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <div class="grid-overlay"></div>
    </div>

    <div class="login-wrap">
      <el-card class="login-card" shadow="always">
        <div class="login-inner">
          <!-- Logo -->
          <div class="logo-box">
            <div class="logo-icon">
              <el-icon :size="30"><DataAnalysis /></el-icon>
            </div>
            <h1 class="title">智能数据 Agent</h1>
            <p class="slogan">让数据开口说话，驱动智能决策</p>
          </div>

          <el-tabs v-model="tab" class="tabs">
            <el-tab-pane label="登录" name="login">
              <el-form @keyup.enter="doLogin" size="large">
                <el-form-item>
                  <el-input
                    v-model="loginForm.username"
                    placeholder="用户名"
                    :prefix-icon="User"
                    clearable
                  />
                </el-form-item>
                <el-form-item>
                  <el-input
                    v-model="loginForm.password"
                    type="password"
                    placeholder="密码"
                    :prefix-icon="Lock"
                    show-password
                  />
                </el-form-item>
                <el-button type="primary" class="full-btn" :loading="loading" @click="doLogin">
                  登 录
                </el-button>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="注册" name="register">
              <el-form @keyup.enter="doRegister" size="large">
                <el-form-item>
                  <el-input
                    v-model="regForm.username"
                    placeholder="用户名（至少 3 位）"
                    :prefix-icon="User"
                    clearable
                  />
                </el-form-item>
                <el-form-item>
                  <el-input
                    v-model="regForm.password"
                    type="password"
                    placeholder="密码（至少 6 位）"
                    :prefix-icon="Lock"
                    show-password
                  />
                </el-form-item>
                <el-form-item>
                  <el-input
                    v-model="regForm.confirm"
                    type="password"
                    placeholder="确认密码"
                    :prefix-icon="Lock"
                    show-password
                  />
                </el-form-item>
                <el-button type="primary" class="full-btn" :loading="loading" @click="doRegister">
                  注 册
                </el-button>
              </el-form>
            </el-tab-pane>
          </el-tabs>

          <div class="foot">
            <span class="tip">默认管理员：admin / admin123</span>
          </div>
        </div>
      </el-card>

      <div class="footer">
        Powered by 智能数据 Agent · SQL + RAG 智能分析
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, DataAnalysis } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const tab = ref('login')
const loading = ref(false)
const loginForm = ref({ username: '', password: '' })
const regForm = ref({ username: '', password: '', confirm: '' })

function afterLogin(role) {
  router.push(role === 'admin' ? '/upload' : '/chat')
}

async function doLogin() {
  if (!loginForm.value.username || !loginForm.value.password) {
    return ElMessage.warning('请输入用户名和密码')
  }
  loading.value = true
  try {
    const data = await auth.login(loginForm.value.username, loginForm.value.password)
    ElMessage.success('登录成功')
    afterLogin(data.role)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

async function doRegister() {
  const { username, password, confirm } = regForm.value
  if (username.length < 3) return ElMessage.warning('用户名至少 3 位')
  if (password.length < 6) return ElMessage.warning('密码至少 6 位')
  if (password !== confirm) return ElMessage.warning('两次密码不一致')
  loading.value = true
  try {
    const data = await auth.register(username, password)
    ElMessage.success('注册成功，已登录')
    afterLogin(data.role)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-view {
  position: relative;
  height: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
  font-family: 'Microsoft YaHei', sans-serif;
}

/* ---- 动态背景 ---- */
.bg { position: absolute; inset: 0; overflow: hidden; }
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  opacity: 0.6;
  animation: float 12s ease-in-out infinite;
}
.orb-1 { width: 480px; height: 480px; background: #40c9ff; top: -120px; left: -80px; }
.orb-2 { width: 420px; height: 420px; background: #9d55ff; bottom: -120px; right: -60px; animation-delay: -4s; }
.orb-3 { width: 320px; height: 320px; background: #f093fb; top: 30%; left: 55%; opacity: 0.35; animation-delay: -8s; }
.grid-overlay {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.04) 1px, transparent 1px);
  background-size: 44px 44px;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(40px, -30px) scale(1.1); }
}

.login-wrap {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: fadeUp .6s ease;
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ---- 玻璃拟态卡片 ---- */
.login-card {
  width: 420px;
  border: 1px solid rgba(255,255,255,.2);
  background: rgba(255,255,255,.92);
  backdrop-filter: blur(18px);
  border-radius: 22px;
  box-shadow: 0 20px 60px rgba(0,0,0,.45);
  overflow: hidden;
}
.login-card :deep(.el-card__body) { padding: 36px 40px 30px; }
.login-inner { display: flex; flex-direction: column; }

/* ---- Logo ---- */
.logo-box { text-align: center; margin-bottom: 22px; }
.logo-icon {
  width: 70px; height: 70px; margin: 0 auto 14px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 20px; color: #fff;
  background: linear-gradient(135deg, #40c9ff, #2b6dff);
  box-shadow: 0 10px 24px rgba(64,201,255,.45);
}
.title {
  font-size: 24px; font-weight: 700; margin: 0;
  background: linear-gradient(90deg, #1b3a5c, #409eff);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}
.slogan { color: #8b95a5; font-size: 13px; margin: 8px 0 0; letter-spacing: .5px; }

/* ---- Tabs ---- */
.tabs :deep(.el-tabs__nav-wrap::after) { height: 1px; background: #eef1f6; }
.tabs :deep(.el-tabs__item) { font-size: 15px; color: #7a8699; }
.tabs :deep(.el-tabs__item.is-active) { color: #2b6dff; font-weight: 600; }
.tabs :deep(.el-tabs__active-bar) { background: linear-gradient(90deg, #40c9ff, #2b6dff); height: 3px; border-radius: 3px; }

/* ---- 输入框 ---- */
.login-view :deep(.el-input__wrapper) {
  border-radius: 10px;
  background: #f4f7fb;
  box-shadow: none;
  transition: all .25s;
}
.login-view :deep(.el-input__wrapper.is-focus) {
  background: #fff;
  box-shadow: 0 0 0 1px #2b6dff inset;
}

/* ---- 按钮 ---- */
.full-btn {
  width: 100%;
  height: 46px;
  margin-top: 6px;
  font-size: 16px;
  letter-spacing: 6px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  background: linear-gradient(90deg, #40c9ff, #2b6dff, #6a11cb);
  background-size: 200% 100%;
  transition: background-position .4s ease, transform .15s ease, box-shadow .3s ease;
  box-shadow: 0 8px 22px rgba(43,109,255,.4);
}
.full-btn:hover {
  background-position: 100% 0;
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(43,109,255,.5);
}

.foot { text-align: center; margin-top: 16px; }
.tip { color: #a5afbf; font-size: 12px; }

.footer {
  margin-top: 22px; color: rgba(255,255,255,.65);
  font-size: 12px; letter-spacing: 1px;
}
</style>
