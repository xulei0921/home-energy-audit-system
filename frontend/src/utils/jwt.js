export const parseJWT = (token) => {
    try {
        // JWT格式: header.payload.signature, 仅解析payload部分
        const payloadBase64 = token.split('.')[1]
        // Base64解码
        const payloadStr = decodeURIComponent(
            atob(payloadBase64)
            .split('')
            .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
            .join('')
        )
        return JSON.parse(payloadStr)  // 返回解析后的payload
    } catch (error) {
        console.error('解析JWT失败', error)
        return null  // 解析失败视为无效token
    }
}

// 判断token是否过期
export const isTokenExpired = (token) => {
    if (!token) return true  // 无token视为过期
    const payload = parseJWT(token)
    if (!payload || !payload.exp) return true  // 无exp字段视为无效token

    const currentTime = Math.floor(Date.now() / 1000)  // 当前时间戳
    return currentTime > payload.exp  // 若当前时间>过期时间，返回true (已过期)
}