APP_NAME=dietapp-frontend
APP_PORT=3000

.PHONY: build run stop clean

build:
	docker build \
		--build-arg NEXT_PUBLIC_API_URL=$(NEXT_PUBLIC_API_URL) \
		--build-arg NEXT_PUBLIC_TRANSCRIPTION_API_URL=$(NEXT_PUBLIC_TRANSCRIPTION_API_URL) \
		-t $(APP_NAME):latest .

run:
	docker run -d \
		--name $(APP_NAME) \
		-p $(APP_PORT):$(APP_PORT) \
		--env-file .env \
		$(APP_NAME):latest

stop:
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true

clean:
	docker rmi $(APP_NAME):latest || true

.env:
	@echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env
	@echo "Created default .env file. Please customize it."

