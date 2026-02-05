<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- Logo e Título -->
      <div class="auth-header">
        <div class="logo">
          <span class="material-icons-outlined">water_drop</span>
        </div>
        <h1>AquaSense</h1>
        <p class="subtitle">Sistema Inteligente de Manutenção de Aquário </p>
      </div>

      <!-- Formulário -->
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="email">Email</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none">
              <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z" fill="currentColor"/>
            </svg>
            <input 
              id="email"
              v-model="form.email"
              type="email"
              placeholder="exemplo@email.com"
              required
              autocomplete="email"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z" fill="currentColor"/>
            </svg>
            <input 
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="********"
              required
              autocomplete="current-password"
            />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              <svg v-if="showPassword" viewBox="0 0 24 24" fill="none">
                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none">
                <path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z" fill="currentColor"/>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="error" class="error-message">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor"/>
          </svg>
          {{ error }}
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Entrar</span>
        </button>
      </form>

      <!-- Link para registo -->
      <div class="auth-footer">
        <p>Não tem conta? <NuxtLink to="/register">Criar conta</NuxtLink></p>
      </div>

      <!-- Decoração -->
      <div class="decoration decoration-1"></div>
      <div class="decoration decoration-2"></div>
    </div>

    <!-- Background animado -->
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

const form = ref({ email: '', password: '' })
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''

  try {
    const response = await $fetch<{ success: boolean; token: string }>('/api/auth/login', {
      method: 'POST',
      body: form.value,
      credentials: 'include'
    })

    if (response.success) {
      router.push('/')
    }
  } catch (err: any) {
    error.value = err.data?.message || 'Erro ao efectuar login'
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
  padding: 48px;
  width: 100%;
  max-width: 420px;
  position: relative;
  z-index: 10;
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(148, 163, 184, 0.05);
}

.auth-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 10px 30px -10px rgba(6, 182, 212, 0.5);
}

.logo .material-icons-outlined {
  font-size: 36px;
  color: white;
}

.auth-header h1 {
  color: #f1f5f9;
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px;
  letter-spacing: -0.5px;
}

.subtitle {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #cbd5e1;
  font-size: 14px;
  font-weight: 500;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 16px;
  width: 20px;
  height: 20px;
  color: #64748b;
  pointer-events: none;
}

.input-wrapper input {
  width: 100%;
  padding: 14px 48px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  color: #f1f5f9;
  font-size: 15px;
  transition: all 0.2s ease;
}

.input-wrapper input::placeholder {
  color: #475569;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #06b6d4;
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
}

.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.toggle-password:hover {
  color: #94a3b8;
}

.toggle-password svg {
  width: 20px;
  height: 20px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 10px;
  color: #fca5a5;
  font-size: 14px;
}

.error-message svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.btn-primary {
  padding: 16px;
  background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 52px;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px -10px rgba(6, 182, 212, 0.5);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
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
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
}

.auth-footer p {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
}

.auth-footer a {
  color: #06b6d4;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.auth-footer a:hover {
  color: #22d3ee;
}

/* Decorações */
.decoration {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.decoration-1 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%);
  top: -100px;
  right: -100px;
}

.decoration-2 {
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
  bottom: -75px;
  left: -75px;
}

/* Background animado */
.bg-animation {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.bubble {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
  animation: float 20s infinite ease-in-out;
}

.bubble:nth-child(1) {
  width: 80px;
  height: 80px;
  left: 10%;
  bottom: -80px;
  animation-delay: 0s;
  animation-duration: 18s;
}

.bubble:nth-child(2) {
  width: 120px;
  height: 120px;
  left: 30%;
  bottom: -120px;
  animation-delay: 2s;
  animation-duration: 22s;
}

.bubble:nth-child(3) {
  width: 60px;
  height: 60px;
  left: 50%;
  bottom: -60px;
  animation-delay: 4s;
  animation-duration: 16s;
}

.bubble:nth-child(4) {
  width: 100px;
  height: 100px;
  left: 70%;
  bottom: -100px;
  animation-delay: 6s;
  animation-duration: 20s;
}

.bubble:nth-child(5) {
  width: 70px;
  height: 70px;
  left: 85%;
  bottom: -70px;
  animation-delay: 8s;
  animation-duration: 24s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) rotate(360deg);
    opacity: 0;
  }
}

/* Responsivo */
@media (max-width: 480px) {
  .auth-card {
    padding: 32px 24px;
    border-radius: 20px;
  }

  .auth-header h1 {
    font-size: 24px;
  }

  .logo {
    width: 56px;
    height: 56px;
  }

  .logo .material-icons-outlined {
    font-size: 32px;
  }
}
</style>
