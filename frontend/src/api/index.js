import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('da_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('da_token')
      localStorage.removeItem('da_username')
      localStorage.removeItem('da_role')
      if (!location.pathname.startsWith('/login')) {
        location.href = '/login'
      }
    }
    return Promise.reject(err)
  },
)

export async function fetchDatasets() {
  const { data } = await api.get('/datasets')
  return data.datasets
}

export function uploadFile(file, type, description) {
  const form = new FormData()
  form.append('file', file)
  form.append('type', type)
  form.append('description', description)
  return api.post('/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } })
}
