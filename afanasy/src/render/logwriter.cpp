#include "logwriter.h"

#include <chrono>
#include <cstring>
#include <sstream>
#include <vector>

#ifndef WINNT
#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#define closesocket close
#else
#include <winsock2.h>
#include <ws2tcpip.h>
#endif

#define AFOUTPUT
#undef AFOUTPUT
#include "../include/macrooutput.h"
#include "../libafanasy/logger.h"

const int MemoryLogWriter::ms_DataSizeMax   = 1 << 20; // 1 MB
const int MemoryLogWriter::ms_DataSizeHalf  = MemoryLogWriter::ms_DataSizeMax >> 1;
const int MemoryLogWriter::ms_DataShiftMin = MemoryLogWriter::ms_DataSizeHalf >> 1;

const char *MemoryLogWriter::ms_overload_string = "\n\
\n\
\n\
\n\
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\
\n\
\n\
\n\
Maximum size reached. Output middle trunctated.\n\
\n\
\n\
\n\
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\
\n\
\n\
\n\
";

MemoryLogWriter::MemoryLogWriter() :
	m_data(nullptr),
	m_datasize(0),
	m_overload(false)
{
	m_data = new char[ms_DataSizeMax];
	m_overload_string_length = int(strlen(ms_overload_string));

	if (m_data == nullptr)
	{
		AFERROR("MemoryLogWriter: Can`t allocate memory for data.")
	}
}

MemoryLogWriter::~MemoryLogWriter()
{
	if (m_data != nullptr)
		delete[] m_data;
}

char *MemoryLogWriter::getData(int *o_size) const
{
	if (o_size != nullptr)
		*o_size = m_datasize;
	return m_data;
}

void MemoryLogWriter::write(const char *i_data, size_t i_size)
{
	if (m_data == nullptr || i_data == nullptr || i_size == 0)
		return;

	const char *copy_data = i_data;
	int copy_size = int(i_size);

	if (m_datasize + copy_size > ms_DataSizeMax)
	{
		if (m_datasize < ms_DataSizeHalf)
		{
			memcpy(m_data + m_datasize, copy_data, ms_DataSizeHalf - m_datasize);
			copy_data = copy_data + ms_DataSizeHalf - m_datasize;
			copy_size = copy_size - (ms_DataSizeHalf - m_datasize);
			m_datasize = ms_DataSizeHalf;
		}

		if (copy_size >= ms_DataSizeHalf)
		{
			copy_data = copy_data + copy_size - ms_DataSizeHalf;
			copy_size = ms_DataSizeHalf;
			m_datasize = ms_DataSizeHalf;
		}
		else
		{
			int shift = m_datasize + copy_size - ms_DataSizeMax;
			if ((shift < ms_DataShiftMin) && (m_datasize > ms_DataSizeHalf + ms_DataShiftMin))
				shift = ms_DataShiftMin;

			int move_size = m_datasize - ms_DataSizeHalf - shift;
			if (move_size > 0)
			{
				memmove(m_data + ms_DataSizeHalf, m_data + ms_DataSizeHalf + shift, move_size);
				m_datasize -= shift;
			}
			else
				AFERRAR("MemoryLogWriter::write: move_size = %d < 0", move_size)
		}

		if (!m_overload)
		{
			strncpy(m_data + ms_DataSizeHalf - m_overload_string_length, ms_overload_string, m_overload_string_length);
			m_overload = true;
		}
	}

	memcpy(m_data + m_datasize, copy_data, copy_size);
	m_datasize += copy_size;
}

// -----------------------------------------------------------------------------
// LokiLogWriter Implementation
// -----------------------------------------------------------------------------

LokiLogWriter::LokiLogWriter(const LogTaskContext &i_ctx, const std::string &i_host, int i_port, const std::string &i_path) :
	m_ctx(i_ctx),
	m_host(i_host),
	m_port(i_port),
	m_path(i_path)
{
}

LokiLogWriter::~LokiLogWriter()
{
	flush();
}

std::string LokiLogWriter::escapeJsonString(const std::string &i_str)
{
	std::ostringstream ss;
	for (char c : i_str)
	{
		switch (c)
		{
			case '"':  ss << "\\\""; break;
			case '\\': ss << "\\\\"; break;
			case '\b': ss << "\\b";  break;
			case '\f': ss << "\\f";  break;
			case '\n': ss << "\\n";  break;
			case '\r': ss << "\\r";  break;
			case '\t': ss << "\\t";  break;
			default:
				if ('\x00' <= c && c <= '\x1f')
				{
					char buf[8];
					snprintf(buf, sizeof(buf), "\\u%04x", c);
					ss << buf;
				}
				else
					ss << c;
		}
	}
	return ss.str();
}

void LokiLogWriter::write(const char *i_data, size_t i_size)
{
	if (i_data == nullptr || i_size == 0)
		return;

	m_remainder.append(i_data, i_size);

	std::vector<std::string> lines;
	size_t pos = 0;
	while (true)
	{
		size_t newline = m_remainder.find('\n', pos);
		if (newline == std::string::npos)
			break;

		lines.push_back(m_remainder.substr(pos, newline - pos));
		pos = newline + 1;
	}

	if (pos > 0)
		m_remainder.erase(0, pos);

	if (lines.empty())
		return;

	// Build Loki REST JSON payload
	auto now_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
		std::chrono::system_clock::now().time_since_epoch()).count();

	std::ostringstream json;
	json << "{\"streams\":[{\"stream\":{";
	json << "\"app\":\"afanasy\"";
	json << ",\"job_id\":\""      << m_ctx.job_id << "\"";
	json << ",\"block_num\":\""   << m_ctx.block_num << "\"";
	json << ",\"task_num\":\""    << m_ctx.task_num << "\"";
	json << ",\"session_num\":\"" << m_ctx.session_num << "\"";
	if (!m_ctx.service.empty())
		json << ",\"service\":\"" << escapeJsonString(m_ctx.service) << "\"";
	if (!m_ctx.host_name.empty())
		json << ",\"host\":\"" << escapeJsonString(m_ctx.host_name) << "\"";
	if (!m_ctx.job_name.empty())
		json << ",\"job_name\":\"" << escapeJsonString(m_ctx.job_name) << "\"";
	json << "},\"values\":[";

	for (size_t i = 0; i < lines.size(); ++i)
	{
		if (i > 0) json << ",";
		json << "[\"" << (now_ns + i) << "\",\"" << escapeJsonString(lines[i]) << "\"]";
	}

	json << "]}]}";

	std::string payload = json.str();

	pushToLoki(payload);
}

void LokiLogWriter::flush()
{
	if (!m_remainder.empty())
	{
		std::string last_line = m_remainder;
		if (last_line.back() != '\n')
			last_line += '\n';
		m_remainder.clear();
		write(last_line.c_str(), last_line.size());
	}
}

void LokiLogWriter::pushToLoki(const std::string &i_json_payload)
{
	struct addrinfo hints, *res = nullptr;
	memset(&hints, 0, sizeof(hints));
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_family = AF_UNSPEC;

	std::string port_str = std::to_string(m_port);
	if (getaddrinfo(m_host.c_str(), port_str.c_str(), &hints, &res) != 0 || res == nullptr)
	{
		AF_WARN << "LokiLogWriter: Unable to resolve " << m_host;
		return;
	}

	int sock = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
	if (sock < 0)
	{
		freeaddrinfo(res);
		return;
	}

	if (connect(sock, res->ai_addr, res->ai_addrlen) < 0)
	{
		AF_WARN << "LokiLogWriter: Unable to connect to " << m_host << ":" << m_port;
		closesocket(sock);
		freeaddrinfo(res);
		return;
	}
	freeaddrinfo(res);

	// Construct HTTP POST request
	std::ostringstream req;
	req << "POST " << m_path << " HTTP/1.1\r\n";
	req << "Host: " << m_host << ":" << m_port << "\r\n";
	req << "Content-Type: application/json\r\n";
	req << "Content-Length: " << i_json_payload.size() << "\r\n";
	req << "Connection: close\r\n\r\n";
	req << i_json_payload;

	std::string req_str = req.str();
#ifdef WINNT
	send(sock, req_str.c_str(), int(req_str.size()), 0);
#else
	ssize_t written = ::write(sock, req_str.c_str(), req_str.size());
	(void)written;
#endif

	closesocket(sock);
}
