backend_shell:
	docker exec -it cook_backend sh

psql:
	docker exec -it cook_db psql -U postgres
