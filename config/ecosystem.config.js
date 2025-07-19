module.exports = {
  apps: [
    {
      name: 'touchline-backend',
      script: 'uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000',
      cwd: '/var/www/touchline/backend',
      interpreter: '/var/www/touchline/backend/venv/bin/python',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: '/var/www/touchline/backend'
      },
      error_file: '/var/log/touchline/backend-error.log',
      out_file: '/var/log/touchline/backend-out.log',
      log_file: '/var/log/touchline/backend-combined.log',
      time: true
    },
    {
      name: 'touchline-frontend',
      script: 'npm',
      args: 'start',
      cwd: '/var/www/touchline/frontend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      error_file: '/var/log/touchline/frontend-error.log',
      out_file: '/var/log/touchline/frontend-out.log',
      log_file: '/var/log/touchline/frontend-combined.log',
      time: true
    }
  ]
}; 