#include "logwriter.h"

#include <cstring>
#include "../include/macrooutput.h"

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