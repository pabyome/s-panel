<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-gray-900">Swarm Management</h1>
      <div v-if="swarmInfo.active" class="flex gap-2">
         <button @click="leaveSwarm" class="rounded-md bg-red-50 px-3 py-2 text-sm font-semibold text-red-600 shadow-sm ring-1 ring-inset ring-red-300 hover:bg-red-100">Leave Swarm</button>
      </div>
    </div>

    <!-- Not Active State -->
    <div v-if="!swarmInfo.active" class="rounded-lg bg-white p-12 text-center shadow-sm ring-1 ring-gray-900/5">
      <h3 class="mt-2 text-sm font-semibold text-gray-900">Swarm Not Initialized</h3>
      <p class="mt-1 text-sm text-gray-500">This node is not part of a Docker Swarm cluster.</p>
      <div class="mt-6">
        <button @click="initSwarm" type="button" class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
          <PlusIcon class="-ml-0.5 mr-1.5 h-5 w-5" aria-hidden="true" />
          Initialize Swarm
        </button>
      </div>
    </div>

    <!-- Active State -->
    <div v-else class="space-y-6">
        <!-- Info Card -->
        <div class="rounded-lg bg-white p-6 shadow-sm ring-1 ring-gray-900/5">
            <dl class="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2">
                <div class="sm:col-span-1">
                    <dt class="text-sm font-medium text-gray-500">Cluster ID</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{ swarmInfo.cluster_id }}</dd>
                </div>
                <div class="sm:col-span-1">
                    <dt class="text-sm font-medium text-gray-500">Role</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{ swarmInfo.is_manager ? 'Manager' : 'Worker' }}</dd>
                </div>
                <div class="sm:col-span-1">
                    <dt class="text-sm font-medium text-gray-500">Nodes</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{ swarmInfo.nodes }}</dd>
                </div>
            </dl>
        </div>

        <!-- Nodes List -->
        <div class="rounded-lg bg-white shadow-sm ring-1 ring-gray-900/5">
            <div class="border-b border-gray-200 px-4 py-5 sm:px-6">
                <h3 class="text-base font-semibold leading-6 text-gray-900">Nodes</h3>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-300">
                    <thead class="bg-gray-50">
                        <tr>
                            <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Hostname</th>
                            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Role</th>
                            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Availability</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 bg-white">
                        <tr v-for="node in nodes" :key="node.id">
                            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{ node.hostname }}</td>
                            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ node.role }}</td>
                            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                <span :class="[node.status === 'ready' ? 'text-green-700 bg-green-50 ring-green-600/20' : 'text-red-700 bg-red-50 ring-red-600/10', 'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset']">{{ node.status }}</span>
                            </td>
                            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ node.availability }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Services List -->
        <div class="rounded-lg bg-white shadow-sm ring-1 ring-gray-900/5">
            <div class="border-b border-gray-200 px-4 py-5 sm:px-6">
                <h3 class="text-base font-semibold leading-6 text-gray-900">Services</h3>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-300">
                    <thead class="bg-gray-50">
                        <tr>
                            <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Name</th>
                            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Image</th>
                            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Replicas</th>
                            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Mode</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 bg-white">
                         <tr v-for="service in services" :key="service.id">
                            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{ service.name }}</td>
                            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ service.image }}</td>
                            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ service.replicas }}</td>
                             <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ Object.keys(service.mode)[0] }}</td>
                        </tr>
                        <tr v-if="services.length === 0">
                            <td colspan="4" class="py-4 text-center text-sm text-gray-500">No services found.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { PlusIcon } from '@heroicons/vue/20/solid'
import axios from 'axios'

const swarmInfo = ref({ active: false })
const nodes = ref([])
const services = ref([])

const fetchSwarmInfo = async () => {
    try {
        const response = await axios.get('/api/v1/swarm/info')
        swarmInfo.value = response.data
        if (swarmInfo.value.active) {
            fetchDetails()
        }
    } catch (e) {
        console.error("Failed to fetch swarm info", e)
    }
}

const fetchDetails = async () => {
    try {
        const [nodesRes, servicesRes] = await Promise.all([
            axios.get('/api/v1/swarm/nodes'),
            axios.get('/api/v1/swarm/services')
        ])
        nodes.value = nodesRes.data
        services.value = servicesRes.data
    } catch (e) {
        console.error("Failed to fetch swarm details", e)
    }
}

const initSwarm = async () => {
    try {
        await axios.post('/api/v1/swarm/init')
        fetchSwarmInfo()
    } catch (e) {
        alert("Failed to init swarm: " + (e.response?.data?.detail || e.message))
    }
}

const leaveSwarm = async () => {
    if(!confirm("Are you sure you want to leave the swarm? Services running on this node will be lost.")) return;
    try {
        await axios.post('/api/v1/swarm/leave?force=true')
        fetchSwarmInfo()
        nodes.value = []
        services.value = []
    } catch (e) {
        alert("Failed to leave swarm: " + (e.response?.data?.detail || e.message))
    }
}

onMounted(() => {
    fetchSwarmInfo()
})
</script>
