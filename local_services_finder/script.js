// Local Services Finder - localStorage persistence
const STORAGE_KEY = 'local_services_finder.services'

function uid(){return Math.random().toString(36).slice(2,9)}

function getServices(){
  try{
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw? JSON.parse(raw): []
  }catch(e){
    console.error('Failed to parse services',e)
    return []
  }
}

function saveServices(list){
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
}

function render(){
  const list = getServices()
  const container = document.getElementById('services-list')
  const emptyNote = document.getElementById('empty-note')
  container.innerHTML = ''
  if(!list.length){
    emptyNote.style.display = 'block'
    return
  }
  emptyNote.style.display = 'none'
  list.forEach(item=>{
    const li = document.createElement('li')
    li.className = 'service-item'
    li.dataset.id = item.id
    li.innerHTML = `
      <div>
        <div class="service-title">${escapeHtml(item.name)}</div>
        <div class="service-meta">${escapeHtml(item.category || '')}</div>
        <div class="service-meta">${escapeHtml(item.phone || '')}</div>
        <div class="service-meta">${escapeHtml(item.address || '')}</div>
      </div>
      <div class="item-actions">
        <button class="small-btn edit">Edit</button>
        <button class="small-btn delete">Delete</button>
      </div>
    `
    container.appendChild(li)
  })
}

function escapeHtml(s){
  if(!s) return ''
  return s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')
}

function addService(data){
  const list = getServices()
  list.unshift(data)
  saveServices(list)
  render()
}

function updateService(id, data){
  const list = getServices()
  const idx = list.findIndex(x=>x.id===id)
  if(idx===-1) return
  list[idx] = Object.assign({}, list[idx], data)
  saveServices(list)
  render()
}

function deleteService(id){
  let list = getServices()
  list = list.filter(x=>x.id!==id)
  saveServices(list)
  render()
}

// Wire up form
const form = document.getElementById('service-form')
let editingId = null

form.addEventListener('submit', e=>{
  e.preventDefault()
  const data = {
    id: editingId || uid(),
    name: form.name.value.trim(),
    category: form.category.value.trim(),
    phone: form.phone.value.trim(),
    address: form.address.value.trim(),
    created_at: new Date().toISOString()
  }
  if(!data.name){
    alert('Please enter a service name')
    return
  }
  if(editingId){
    updateService(editingId, data)
    editingId = null
    form.querySelector('button[type=submit]').textContent = 'Add Service'
  }else{
    addService(data)
  }
  form.reset()
})

// Clear all
document.getElementById('clear-all').addEventListener('click', ()=>{
  if(!confirm('Remove all saved services?')) return
  localStorage.removeItem(STORAGE_KEY)
  render()
})

// Delegated list actions
document.getElementById('services-list').addEventListener('click', e=>{
  const li = e.target.closest('li')
  if(!li) return
  const id = li.dataset.id
  if(e.target.classList.contains('delete')){
    if(confirm('Delete this service?')) deleteService(id)
  }else if(e.target.classList.contains('edit')){
    const svc = getServices().find(x=>x.id===id)
    if(!svc) return
    form.name.value = svc.name
    form.category.value = svc.category
    form.phone.value = svc.phone
    form.address.value = svc.address
    editingId = id
    form.querySelector('button[type=submit]').textContent = 'Save'
    window.scrollTo({top:0,behavior:'smooth'})
  }
})

// Initial render
render()
