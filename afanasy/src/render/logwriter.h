#pragma once

#include <cstddef>
#include <string>

class LogWriter
{
public:
	virtual ~LogWriter() = default;

	// Writes a chunk of log output that has already been processed by the Python parser
	virtual void write(const char *i_data, size_t i_size) = 0;

	// Retrieves accumulated log data (used by afserver MCTaskUp; returns NULL if backend streams remotely)
	virtual char *getData(int *o_size) const = 0;
};

// Default backend: in-memory circular shift buffer with 1MB maximum size
class MemoryLogWriter : public LogWriter
{
public:
	MemoryLogWriter();
	virtual ~MemoryLogWriter();

	void write(const char *i_data, size_t i_size) override;
	char *getData(int *o_size) const override;

private:
	char *m_data;
	int m_datasize;
	bool m_overload;
	int m_overload_string_length;

	static const int ms_DataSizeMax;
	static const int ms_DataSizeHalf;
	static const int ms_DataShiftMin;
	static const char *ms_overload_string;
};
