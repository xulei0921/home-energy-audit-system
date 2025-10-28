<template>
    <div class="login-container">
        <el-card class="login-card">
            <template #header>
                <div class="login-header">
                    <h2>家庭能耗体检系统</h2>
                    <p>登录您的账户</p>
                </div>
            </template>

            <el-form
                :model="loginForm"
                :rules="loginRules"
                ref="loginFormRef"
            >
                <el-form-item label="用户名:">
                    <el-input
                        :prefix-icon="User"
                        v-model="loginForm.username"
                        placeholder="请输入用户"
                    >
                    </el-input>
                </el-form-item>
                <el-form-item label="密码:">
                    <el-input
                        :prefix-icon="Lock"
                        v-model="loginForm.password"
                        type="password"
                        placeholder="请输入密码"
                        show-password
                    ></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button
                        type="primary"
                        @click="handleLogin"
                    >
                        登录
                    </el-button>
                </el-form-item>
            </el-form>

            <div class="login-footer">
                <p>还没有账户? <el-link type="primary">立即注册</el-link></p>
            </div>
        </el-card>

        <!-- 注册对话框 -->
        
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { User, Lock } from '@element-plus/icons-vue'
import { loginUser } from '@/api/user';
import { useUserStore } from '@/stores';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';

const userStore = useUserStore()

const {
    setToken,
    removeToken,
} = userStore

const {
    token
} = storeToRefs(userStore)

const router = useRouter()

const loginForm = ref({
    username: '',
    password: ''
})

const handleLogin = async () => {
    try {
        const data = await loginUser(loginForm.value)
        console.log(data)
        setToken(data.access_token)
        ElMessage.success('登录成功')
        router.push('/index')
    } catch (error) {
        console.error(error)
    }
}
</script>

<style scoped>

</style>