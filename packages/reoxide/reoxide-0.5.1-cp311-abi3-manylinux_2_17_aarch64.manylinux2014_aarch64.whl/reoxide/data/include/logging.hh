#pragma once
#define LOG_ERROR(...) log(LEVEL_ERROR, __VA_ARGS__);
#define LOG_WARN(...) log(LEVEL_WARN, __VA_ARGS__);
#define LOG_INFO(...) log(LEVEL_INFO, __VA_ARGS__);
#define LOG_DEBUG(...) log(LEVEL_DEBUG, __VA_ARGS__);
#define LOG_ASSERT(x, msg)                                           \
  if (!(x)) {                                                        \
    LOG_ERROR("assert at %s, line %d: %s", __FILE__, __LINE__, msg); \
    std::exit(1);                                                    \
  }

enum LogLevel : unsigned char {
  LEVEL_DEBUG,
  LEVEL_INFO,
  LEVEL_WARN,
  LEVEL_ERROR,
  LEVEL_COUNT
};

void initialize_log();
void close_log();
void log(LogLevel level, const char* fmt, ...);
