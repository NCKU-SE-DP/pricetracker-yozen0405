<template>
    <div class="register-page">
        <div class="container">
            <div class="form-box">
                <h1 :style="{ '--progress-width': progressWidth + '%' }">使用者註冊</h1>
                <form @submit.prevent="register">
                    <div class="input-field">
                        <label class="text-field">
                            <span>Username</span>
                        </label>
                        <input v-model="username" type="text" @input="updateProgress" required>
                        <p v-if="errors.username" class="error">{{ errors.username }}</p>
                    </div>

                    <div class="input-field">
                        <label class="text-field">
                            <span>Password</span>
                        </label>
                        <input v-model="password" type="password" @input="updateProgress" required>
                    <p v-if="errors.password" class="error">{{ errors.password }}</p>
                    </div>

                    <div class="input-field">
                        <label class="text-field">
                            <span>Password confirm</span>
                        </label>
                        <input v-model="passwordConfirm" type="password" @input="updateProgress" required>
                    <p v-if="errors.passwordConfirm" class="error">{{ errors.passwordConfirm }}</p>
                    </div>

                    <div class="ops">
                        <button type="submit" class="register-btn" id="register">註冊</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth';

export default {
    data() {
        return {
            username: '',
            password: '',
            passwordConfirm: '',
            errors: {
                username: '',
                password: '',
                passwordConfirm: ''
            },
            progressWidth: 0
        };
    },
    methods: {
        register() {
            if (this.validate()) {
                const userStore = useAuthStore();
                userStore.register(this.username, this.password);
            }
        },
        validate() {
            let valid = true;
            this.errors = { username: '', password: '', passwordConfirm: '' };

            if (!this.username.trim()) {
                this.errors.username = 'Username is required.';
                valid = false;
            }
            if (!this.password) {
                this.errors.password = 'Password is required.';
                valid = false;
            }
            if (this.password !== this.passwordConfirm) {
                this.errors.passwordConfirm = 'Passwords do not match!';
                valid = false;
            }
            return valid;
        }, 
        updateProgress() {
          let tmp = 0;
          if (this.username.length) {
            tmp += Math.ceil(100 / 3);
          }
          if (this.password.length) {
            tmp += Math.ceil(100 / 3);
          }
          if (this.passwordConfirm.length) {
            tmp += Math.ceil(100 / 3);
          }
          this.progressWidth = Math.min(tmp, 100);
        }
    }
}
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 4.5em);
  height: calc(100% - 4.5em);
  box-sizing: border-box;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
}

.container {
  max-width: 600px;
  width: 100%;
  padding: 2em;
  background-color: white;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  text-align: center;
  transform: translateY(-10%);
}

.form-box h1 {
  font-size: 2em;
  margin-bottom: .3em;
  color: #343a40;
  position: relative;
}

.form-box h1::after {
  content: '';
  display: block;
  width: var(--progress-width, 0%);
  height: 4px;
  background-color: #5bc0de;
  transition: width 0.5s ease;
  margin: .4em 0 1em;
}

.input-field {
  position: relative;
  margin-bottom: 2em;
  display: flex;
  flex-direction: column;
}

.text-field {
  display: flex;
  align-items: center;
  color: #6c757d;
  font-size: 0.9em;
}

.input-field input {
  width: 100%;
  padding: 0.75em 0 .3em 0;
  font-size: 1.3em;
  border: none;
  border-bottom: 2px solid #ced4da;
  outline: none;
  transition: border-color 0.3s ease;
}

.input-field:focus-within label span {
  color: #2d2d2e; 
}

.input-field input:focus {
  border-bottom-color: #8d8f92;
}

.error {
  color: #dc3545;
  font-size: 0.9em;
  margin-bottom: 1em;
}

.ops {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1em;
}

.ops button {
  flex: 1;
  padding: 0.5em 1.5em;
  font-size: 1.1em;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.register-btn {
  background-color: #5bc0de;
  color: white;
}

.register-btn:hover {
  background-color: #46b8da;
}

/* Responsive design */
@media (max-width: 768px) {
  .register-page {
    align-items: flex-start;
  }

  .container {
    padding: 1.5em;
    background: none;
    box-shadow: none;
    transform: none;
  }
}
</style>