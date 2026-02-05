<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo">
          <span class="material-icons-outlined">water_drop</span>
        </div>
        <h1>Criar Conta</h1>
        <p class="subtitle">Junte-se ao AquaSense</p>
      </div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="nome">Nome</label>
          <div class="input-wrapper">
            <span class="material-icons-outlined input-icon">person</span>
            <input id="nome" v-model="form.nome" type="text" placeholder="O seu nome" required autocomplete="name" />
          </div>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <div class="input-wrapper">
            <span class="material-icons-outlined input-icon">email</span>
            <input id="email" v-model="form.email" type="email" placeholder="exemplo@email.com" required autocomplete="email" />
          </div>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <div class="input-wrapper">
            <span class="material-icons-outlined input-icon">lock</span>
            <input id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'" placeholder="Mínimo 6 caracteres" required minlength="6" autocomplete="new-password" />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <span class="material-icons-outlined">{{ showPassword ? 'visibility' : 'visibility_off' }}</span>
            </button>
          </div>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirmar Password</label>
          <div class="input-wrapper">
            <span class="material-icons-outlined input-icon">lock</span>
            <input id="confirmPassword" v-model="form.confirmPassword" :type="showPassword ? 'text' : 'password'" placeholder="Repita a password" required autocomplete="new-password" />
          </div>
        </div>

        <div v-if="error" class="error-message">
          <span class="material-icons-outlined">error</span>
          {{ error }}
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Criar Conta</span>
        </button>
      </form>

      <div class="auth-footer">
        <p>Já tem conta? <NuxtLink to="/login">Entrar</NuxtLink></p>
      </div>

      <div class="decoration decoration-1"></div>
      <div class="decoration decoration-2"></div>
    </div>

    <div class="bg-animation">
      <div class="bubble"></div>
      <div class="bubble"></div>
      <div class="bubble"></div>
      <div class="bubble"></div>
      <div class="bubble"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
const router = useRouter()

const form = ref({
  nome: '',
  email: '',
  password: '',
  confirmPassword: ''
})
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  error.value = ''

  if (form.value.password !== form.value.confirmPassword) {
    error.value = 'As passwords não coincidem'
    return
  }

  if (form.value.password.length < 6) {
    error.value = 'Password deve ter pelo menos 6 caracteres'
    return
  }

  loading.value = true

  try {
    const response = await $fetch<{ success: boolean; token: string }>('/api/auth/register', {
      method: 'POST',
      body: {
        nome: form.value.nome,
        email: form.value.email,
        password: form.value.password
      }
    })

    if (response.success && response.token) {
      localStorage.setItem('auth_token', response.token)
      router.push('/')
    }
  } catch (err: any) {
    error.value = err.data?.message || 'Erro ao criar conta'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
  font-family: 'Inter', sans-serif;
}

.auth-card {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 24px;
  padding: 40px 36px;
  width: 100%;
  max-width: 420px;
  position: relative;
  z-index: 10;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(148, 163, 184, 0.05);
}

.auth-header {
  text-align: center;
  margin-bottom: 28px;
}

.logo {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  box-shadow: 0 10px 30px -10px rgba(16, 185, 129, 0.5);
}

.logo .material-icons-outlined {
  font-size: 32px;
  color: white;
}

.auth-header h1 {
  color: #f1f5f9;
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 6px;
}

.subtitle {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  color: #cbd5e1;
  font-size: 13px;
  font-weight: 500;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  font-size: 20px;
  color: #64748b;
  pointer-events: none;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 14px 12px 44px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  color: #f1f5f9;
  font-size: 14px;
  transition: all 0.2s ease;
}

.input-wrapper input::placeholder {
  color: #475569;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.toggle-password {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  padding: 6px;
  cursor: pointer;
  color: #64748b;
  display: flex;
  transition: color 0.2s;
}

.toggle-password:hover {
  color: #94a3b8;
}

.toggle-password .material-icons-outlined {
  font-size: 20px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 10px;
  color: #fca5a5;
  font-size: 13px;
}

.error-message .material-icons-outlined {
  font-size: 18px;
}

.btn-primary {
  padding: 14px;
  background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 6px;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px -10px rgba(16, 185, 129, 0.5);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
}

.auth-footer p {
  color: #94a3b8;
  font-size: 13px;
  margin: 0;
}

.auth-footer a {
  color: #10b981;
  text-decoration: none;
  font-weight: 500;
}

.auth-footer a:hover {
  color: #34d399;
}

.decoration {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.decoration-1 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, transparent 70%);
  top: -100px;
  right: -100px;
}

.decoration-2 {
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%);
  bottom: -75px;
  left: -75px;
}

.bg-animation {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.bubble {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(6, 182, 212, 0.04) 100%);
  animation: float 20s infinite ease-in-out;
}

.bubble:nth-child(1) { width: 80px; height: 80px; left: 10%; bottom: -80px; animation-delay: 0s; animation-duration: 18s; }
.bubble:nth-child(2) { width: 120px; height: 120px; left: 30%; bottom: -120px; animation-delay: 2s; animation-duration: 22s; }
.bubble:nth-child(3) { width: 60px; height: 60px; left: 50%; bottom: -60px; animation-delay: 4s; animation-duration: 16s; }
.bubble:nth-child(4) { width: 100px; height: 100px; left: 70%; bottom: -100px; animation-delay: 6s; animation-duration: 20s; }
.bubble:nth-child(5) { width: 70px; height: 70px; left: 85%; bottom: -70px; animation-delay: 8s; animation-duration: 24s; }

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
}

@media (max-width: 480px) {
  .auth-card { padding: 28px 20px; border-radius: 20px; }
  .auth-header h1 { font-size: 22px; }
  .logo { width: 56px; height: 56px; }
  .logo .material-icons-outlined { font-size: 28px; }
}
</style>
