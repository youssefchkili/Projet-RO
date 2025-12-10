import requests

try:
    resp = requests.get('http://localhost:5000/api/tasks')
    if resp.status_code == 200:
        tasks = resp.json()
        print(f'Found {len(tasks)} tasks')
        for task in tasks:
            print(f'  - {task["title"]}: {task["status"]}')
            requests.put(f'http://localhost:5000/api/tasks/{task["id"]}', 
                        json={'status': 'pending', 'assignedTo': None})
        print('\nAll tasks reset to pending!')
        
        # Clear routes too
        requests.delete('http://localhost:5000/api/routes')
        print('Routes cleared!')
    else:
        print('ERROR: Backend not running on port 5000')
        print('Start the backend first: cd backend && python main.py')
except Exception as e:
    print(f'Error: {e}')
    print('\nMake sure the backend is running on port 5000')
