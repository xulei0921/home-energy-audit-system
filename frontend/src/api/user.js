import request from '@/utils/request'

// 用户登录
export const loginUser = ({ username, password }) => {
    const formData = `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    return request.post('/users/login', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
}