package com.portfolio.ticketing.common;

import java.time.Instant;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ApiExceptionHandler {

	@ExceptionHandler(BusinessException.class)
	ResponseEntity<Map<String, Object>> handleBusinessException(BusinessException exception) {
		return ResponseEntity.status(exception.status()).body(Map.of(
				"timestamp", Instant.now(),
				"code", exception.code(),
				"message", exception.getMessage()));
	}

	@ExceptionHandler(MethodArgumentNotValidException.class)
	ResponseEntity<Map<String, Object>> handleValidationException(MethodArgumentNotValidException exception) {
		String message = exception.getBindingResult().getFieldErrors().stream()
				.findFirst()
				.map(error -> error.getField() + ": " + error.getDefaultMessage())
				.orElse("Invalid request");
		return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of(
				"timestamp", Instant.now(),
				"code", "INVALID_REQUEST",
				"message", message));
	}
}
