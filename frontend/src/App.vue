<template>
  <div v-if="isLoginPage" class="login-page">
    <router-view />
  </div>
  <el-container v-else class="app">
    <el-aside width="220px" class="aside">
      <div class="logo">智能数据 Agent</div>
      <el-menu :default-active="$route.path" router class="menu">
        <el-menu-item v-if="auth.isAdmin" index="/upload">
          <el-icon><Upload /></el-icon>
          <span>数据管理</span>
        </el-menu-item>
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>Agent 对话</span>
        </el-menu-item>
        <el-menu-item index="/chart">
          <el-icon><DataLine /></el-icon>
          <span>图表可视化</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span class="page-title">{{ $route.meta.title || '' }}</span>
        <div class="user-box">
          <el-tag :type="auth.isAdmin ? 'danger' : 'info'" size="small">
            {{ auth.isAdmin ? '管理员' : '客户端' }}
          </el-tag>
          <span class="uname">{{ auth.username }}</span>
          <el-button link type="primary" @click="onLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Upload, ChatDotRound, DataLine } from '@element-plus/icons-vue'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const isLoginPage = computed(() => route.path === '/login')

function onLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, #app { height: 100%; }
body { font-family: 'Microsoft YaHei', sans-serif; background: #f5f7fa; }
.app { height: 100%; }
.aside { background: #fff; border-right: 1px solid #e6e6e6; }
.logo {
  height: 60px; line-height: 60px; text-align: center;
  font-size: 18px; font-weight: 700; color: #409eff;
  border-bottom: 1px solid #f0f0f0;
}
.menu { border-right: none; }
.header {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; border-bottom: 1px solid #e6e6e6;
}
.page-title { font-weight: 600; color: #333; }
.user-box { display: flex; align-items: center; gap: 10px; }
.uname { color: #333; font-weight: 600; }
.main { padding: 0; overflow: hidden; }
.login-page { height: 100%; }
</style>
