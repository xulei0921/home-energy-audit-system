<template>
  <div id="app">
    <el-container v-if="isLogin()">
      <el-header>
        <div class="header-content">
          <div class="logo">
            <h2>家庭能耗体检系统</h2>
          </div>
          <el-menu
            mode="horizontal"
            :default-active="$route.path"
            router
            class="nav-menu"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/devices">设备管理</el-menu-item>
            <el-menu-item index="/audit">能耗报告</el-menu-item>
            <el-menu-item index="/settings">个人设置</el-menu-item>
          </el-menu>
          <div class="user-info">
            <el-dropdown>
              <span class="user-dropdown">
                <el-icon><User /></el-icon>
                admin
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
    <router-view v-else />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from './stores';
import { User, ArrowDown } from '@element-plus/icons-vue'

const userStore = useUserStore()

const {
  isLogin
} = userStore

const fetchCurrentUser = async () => {

}
</script>

<style scoped>
/* * {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
} */

#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.logo h2 {
  color: #409eff;
  margin: 0;
}

.nav-menu {
  flex: 1;
  justify-content: center;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-dropdown:hover {
  background-color: #f5f7fa;
}

.el-main {
  padding: 0;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>