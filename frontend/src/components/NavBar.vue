<template>
  <div :class="{ active: isMenuActive, 'navbar-container': true }">
    <header>
      <RouterLink class="nav-title" to="/overview">價格追蹤小幫手</RouterLink>
      <div class="hamburger" @click="toggleMenu">
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
      </div>
    </header>
    <nav :class="{ active: isMenuActive }">
      <RouterLink to="/overview" @click="closeMenu">物價概覽</RouterLink>
      <RouterLink to="/trending" @click="closeMenu">物價趨勢</RouterLink>
      <RouterLink to="/news" @click="closeMenu">相關新聞</RouterLink>
      <RouterLink v-if="!isLoggedIn" to="/login" @click="closeMenu">登入</RouterLink>
      <span v-else @click="logout; closeMenu">Hi, {{ getUserName }}! 登出</span>
    </nav>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth';

export default {
  name: 'NavBar',
  data() {
    return {
      isMenuActive: false,
    };
  },
  computed: {
    isLoggedIn() {
      const userStore = useAuthStore();
      return userStore.isLoggedIn;
    },
    getUserName() {
      const userStore = useAuthStore();
      return userStore.getUserName;
    },
  },
  methods: {
    toggleMenu() {
      this.isMenuActive = !this.isMenuActive;
    },
    closeMenu() {
      this.isMenuActive = false;
    },
    logout() {
      const userStore = useAuthStore();
      userStore.logout();
    },
  },
};
</script>

<style scoped>
.navbar-container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgb(243, 243, 243);
  padding: 1.5em;
  height: 4.5em;
  width: 100%;
  box-shadow: 0 0 5px #000000;
}

.nav-title {
  font-size: 1.4em;
  font-weight: bold;
  text-decoration: none;
  color: #2c3e50 !important;
}

nav a {
  text-decoration: none;
  color: #575B5D;
  margin: 0 .5em;
  font-size: 1.2em;
}

.hamburger {
  display: none;
  flex-direction: column;
  cursor: pointer;
}

.hamburger .line {
  width: 25px;
  height: 3px;
  background-color: #333;
  margin: 4px 0;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.navbar-container.active .hamburger .line:nth-child(1) {
  transform: rotate(-45deg) translate(-7px, 9px);
}

.navbar-container.active .hamburger .line:nth-child(2) {
  opacity: 0;
}

.navbar-container.active .hamburger .line:nth-child(3) {
  transform: rotate(45deg) translate(-6px, -8px);
}

@media (max-width: 768px) {
  .navbar-container {
    flex-direction: column;
    padding: 0;
    justify-content: unset;
    height: auto;
    box-shadow: 0 0 5px #000000;
  }

  header {
    display: flex;
    justify-content: space-between;
    width: 100%;
    align-items: center;
    background-color: rgb(243, 243, 243);
    padding: 1.5em;
    height: 4.5em;
  }

  .hamburger {
    display: flex;
  }

  nav {
    display: none;
    flex-direction: column;
    background-color: rgb(243, 243, 243);
    width: 100%;
  }

  nav a {
    padding: 0.9em;
    margin: 0;
    text-align: center;
    display: block;
    font-size: 1.2em;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    color: #575b5d;
    z-index: 100;
    transition: background-color 0.3s;
  }

  nav a:first-child {
    border-top: 1px solid rgba(0, 0, 0, 0.1);
  }

  nav a:hover {
    background-color: rgba(224, 223, 223, 0.827);
  }

  .navbar-container.active nav {
    display: flex;
    animation: slideDown 0.3s ease-out forwards;
  }

  @keyframes slideDown {
    0% {
      opacity: 0;
      transform: translateY(-10px);
    }
    100% {
      opacity: 1;
      transform: translateY(0);
    }
  }
}
</style>