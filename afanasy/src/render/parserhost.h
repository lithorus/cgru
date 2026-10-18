#pragma once

#include "../include/afjob.h"

#include "../libafanasy/name_af.h"
#include "logwriter.h"

class ParserHost
{

public:

	ParserHost( af::Service * i_service, LogWriter * i_log_writer = nullptr);
	~ParserHost();

	void read(const std::string & i_mode, int i_pid, std::string & io_output, const std::string & i_resources);

	inline int getPercent()           const { return m_percent;         }
	inline int getFrame()             const { return m_frame;           }
	inline int getPercentFrame()      const { return m_percentframe;    }
	inline bool hasProgressChanged()  const { return m_progress_changed;}
	inline bool hasWarning()          const { return m_warning;         }
	inline bool hasError()            const { return m_error;           }
	inline bool hasFatalError()       const { return m_fatalerror;      }
	inline bool isBadResult()         const { return m_badresult;       }
	inline bool isFinishedSuccess()   const { return m_finishedsuccess; }
	inline std::string getActivity()  const { return m_activity;        }
	inline std::string getResources() const { return m_resources;       }
	inline std::string getReport()    const { return m_report;          }
	inline char* getData( int *size ) const { return m_log_writer ? m_log_writer->getData(size) : nullptr; }
	inline LogWriter* getLogWriter() const { return m_log_writer; }

private:
	af::Service * m_service;
	LogWriter   * m_log_writer;
	bool          m_own_log_writer;

	int  m_percent;
	int  m_frame;
	int  m_percentframe;
	bool m_progress_changed;
	bool m_error;
	bool m_fatalerror;
	bool m_warning;
	bool m_badresult;
	bool m_finishedsuccess;
	std::string m_activity;
	std::string m_resources;
	std::string m_report;

	char*              m_data;
	int                m_datasize;
	static const int   ms_DataSizeMax;
	static const int   ms_DataSizeHalf;
	static const int   ms_DataShiftMin;
	bool               m_overload;
	static const char* ms_overload_string;
	int                m_overload_string_length;

private:
	void parse(const std::string & i_mode, int i_pid, std::string & io_output, const std::string & i_resources);
};
