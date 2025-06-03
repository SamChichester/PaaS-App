<template>
  <div class="flex items-center justify-center min-h-screen">
    <div class="container mx-auto p-4 text-center">
      <h1 class="text-4xl font-bold mb-4">PaaS Deployment</h1>
      <div v-if="loading" class="flex items-center justify-center">
        <svg aria-hidden="true" class="w-8 h-8 text-white animate-spin fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/>
          <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/>
        </svg>
        <span class="sr-only">Loading...</span>
      </div>
      <button class="bg-blue-500 hover:bg-blue-700 text-white py-2 px-4 rounded" v-else-if="!authorized" @click="login">Login with GitHub</button>

      <div v-else>
        <h2>Welcome, {{ username }}</h2>
        <h3 class="mb-3">Your Repositories:</h3>
        <ul class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-4">
          <li v-for="repo in repos" :key="repo.id" class="p-4 bg-gray-100 rounded shadow shadow-md transition">
            <div class="font-semibold mb-2 flex items-center justify-between">
              <span>{{ repo.name }}</span>
              <a
                :href="repo.html_url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-gray-500 hover:text-blue-600 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path
                    d="M12 0C5.37 0 0 5.373 0 12a12 12 0 008.205 11.386c.6.111.82-.258.82-.577v-2.165c-3.338.727-4.033-1.416-4.033-1.416-.546-1.385-1.333-1.754-1.333-1.754-1.09-.744.082-.729.082-.729 1.205.086 1.838 1.237 1.838 1.237 1.07 1.835 2.807 1.305 3.492.997.108-.775.42-1.305.763-1.605-2.665-.305-5.466-1.332-5.466-5.93 0-1.31.468-2.38 1.236-3.22-.124-.305-.536-1.534.117-3.194 0 0 1.008-.322 3.3 1.23a11.51 11.51 0 013.003-.403 11.51 11.51 0 013.003.403c2.292-1.552 3.3-1.23 3.3-1.23.653 1.66.242 2.89.118 3.194.77.84 1.235 1.91 1.235 3.22 0 4.61-2.803 5.623-5.475 5.92.43.37.814 1.102.814 2.222v3.293c0 .32.218.694.825.576A12.005 12.005 0 0024 12c0-6.627-5.373-12-12-12z"
                  />
                </svg>
              </a>
            </div>
            <button 
              :disabled="deploying"
              :class="deploying ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-700'"
              class="text-white py-1 px-2 rounded"
              @click="deploy(repo.clone_url)"
            >
              Deploy
            </button>
          </li>
        </ul>
        <button class="bg-blue-500 hover:bg-blue-700 text-white py-2 px-4 rounded" @click="logout">Logout</button>
      </div>

      <div v-if="output">
        <h3 class="my-3">Deployment Output:</h3>
        <pre class="px-3 py-3 bg-gray-100 rounded whitespace-pre-wrap break-words">{{ output }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      authorized: false,
      username: "",
      repos: [],
      output: null,
      loading: true,
      deploying: false
    }
  },
  methods: {
    async checkAuth() {
      this.loading = true;

      const response = await axios.get(`${import.meta.env.VITE_API_URL}/me`, { withCredentials: true })
      console.log(response)
      this.authorized = response.data.authorized
      if (this.authorized) {
        this.username = response.data.username
        this.fetchRepos()
      }

      this.loading = false;
    },
    login() {
      window.location.href = `${import.meta.env.VITE_API_URL}/login/github?next=${import.meta.env.VITE_APP_URL}`
    },
    logout() {
      window.location.href = `${import.meta.env.VITE_API_URL}/logout`
    },
    async fetchRepos() {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/repos`,  { withCredentials: true })
      this.repos = response.data
    },
    async deploy(repoUrl) {
      this.deploying = true;

      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/deploy`,
        { repo_url: repoUrl },
        { withCredentials: true }
      )
      this.output = response.data.stdout + response.data.stderr

      this.deploying = false;
    },
  },
  mounted() {
    this.checkAuth()
  }
}
</script>