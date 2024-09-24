from app.routes.task_management import generate_unittest_task
result = generate_unittest_task.delay('test_file_path', 'test_task_id')
print(result.id)