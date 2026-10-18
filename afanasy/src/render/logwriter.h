#pragma once

#include <cstddef>
#include <map>
#include <string>

// Context information for identifying log streams in Loki
struct LogTaskContext
{
	int job_id = 0;
	int block_num = 0;
	int task_num = 0;
	int session_num = 0;
	std::string service;
	std::string host_name;
	std::string job_name;
	std::string block_name;
};

// Base abstract interface for handling post-Python task output
class LogWriter
{
public:
	virtual ~LogWriter() = default;

	// Writes log data processed by the Python parser
	virtual void write(const char *i_data, size_t i_size) = 0;

	// Returns buffer data and size for tasks reporting to afserver (nullptr if remote streaming)
	virtual char *getData(int *o_size) const = 0;
};

// Default in-memory buffer implementation that retains the existing 1MB shift-buffer behavior
class MemoryLogWriter : public LogWriter
{
public:
	MemoryLogWriter();
	virtual ~MemoryLogWriter();

	void write(const char *i_data, size_t i_size) override;
	char *getData(int *o_size) const override;

private:
	char *m_data;
	int   m_datasize;
	bool  m_overload;
	int   m_overload_string_length;

	static const int   ms_DataSizeMax;
	static const int   ms_DataSizeHalf;
	static const int   ms_DataShiftMin;
	static const char *ms_overload_string;
};

// Loki REST API ingestion backend (POST /loki/api/v1/push)
class LokiLogWriter : public LogWriter
{
public:
	LokiLogWriter(const LogTaskContext &i_ctx, const std::string &i_host = "127.0.0.1", int i_port = 3100, const std::string &i_path = "/loki/api/v1/push");
	virtual ~LokiLogWriter();

	void write(const char *i_data, size_t i_size) override;
	char *getData(int *o_size) const override { if (o_size) *o_size = 0; return nullptr; }

	void flush();

private:
	void pushToLoki(const std::string &i_json_payload);
	std::string escapeJsonString(const std::string &i_str);

private:
	LogTaskContext m_ctx;
	std::string    m_host;
	int            m_port;
	std::string    m_path;
	std::string    m_remainder;
};
