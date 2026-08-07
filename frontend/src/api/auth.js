import apiClient from './client'

export async function login(username, password) {
  const { data } = await apiClient.post('/auth/login/', { username, password })
  return data
}

export async function logout(refresh) {
  await apiClient.post('/auth/logout/', { refresh })
}
