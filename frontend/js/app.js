let lastUpdateTime = null;
let lastDataHash = null;
let isLoading = false;

function hashData(data) {
    // Простой хеш JS объекта для сравнения
    return JSON.stringify(data).split('').reduce((a, b) => {
        a = ((a << 5) - a) + b.charCodeAt(0);
        return a & a;
    }, 0);
}

function loadUsers() {
    if (isLoading) return; // Предотвращаем одновременные запросы
    
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const table = document.getElementById('users-table');
    const empty = document.getElementById('empty');
    
    loading.style.display = 'block';
    error.style.display = 'none';
    isLoading = true;

    fetch('/api/users')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            loading.style.display = 'none';
            isLoading = false;

            if (data.status === 'success') {
                const currentHash = hashData(data.data);
                
                // Проверяем, изменились ли данные
                if (lastDataHash === currentHash) {
                    // Данные не изменились - не обновляем UI
                    console.log('ℹ️  Данные не изменились, обновление UI пропущено');
                } else {
                    // Данные изменились - обновляем таблицу
                    const users = data.data;
                    const tbody = document.getElementById('users-body');
                    tbody.innerHTML = '';

                    if (users.length === 0) {
                        table.style.display = 'none';
                        empty.style.display = 'block';
                    } else {
                        users.forEach(user => {
                            const row = `
                                <tr>
                                    <td><span class="id">${user.id}</span></td>
                                    <td>${escapeHtml(user.name)}</td>
                                    <td><span class="phone">${escapeHtml(user.phone)}</span></td>
                                    <td><span class="date">${formatDate(user.created_at)}</span></td>
                                </tr>
                            `;
                            tbody.innerHTML += row;
                        });
                        empty.style.display = 'none';
                        table.style.display = 'table';
                    }

                    lastDataHash = currentHash;
                    console.log('✅ Таблица обновлена');
                }

                // Обновляем статистику всегда
                document.getElementById('total-users').textContent = data.count;
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString('ru-RU');
            }
        })
        .catch(err => {
            loading.style.display = 'none';
            isLoading = false;
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = '❌ Ошибка загрузки данных: ' + err.message;
            errorDiv.style.display = 'block';
            console.error('Error:', err);
        });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU') + ' ' + date.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'});
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Загружаем данные при загрузке страницы
window.addEventListener('load', loadUsers);

// Оптимизированный опрос: 10 секунд вместо 5, с проверкой изменений
setInterval(loadUsers, 10000);
