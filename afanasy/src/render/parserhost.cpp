/* ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' *\
 *        .NN.        _____ _____ _____  _    _                 This file is part of CGRU
 *        hMMh       / ____/ ____|  __ \| |  | |       - The Free And Open Source CG Tools Pack.
 *       sMMMMs     | |   | |  __| |__) | |  | |  CGRU is licensed under the terms of LGPLv3, see files
 * <yMMMMMMMMMMMMMMy> |   | | |_ |  _  /| |  | |    COPYING and COPYING.lesser inside of this folder.
 *   `+mMMMMMMMMNo` | |___| |__| | | \ \| |__| |          Project-Homepage: http://cgru.info
 *     :MMMMMMMM:    \_____\_____|_|  \_\\____/        Sourcecode: https://github.com/CGRU/cgru
 *     dMMMdmMMMd     A   F   A   N   A   S   Y
 *    -Mmo.  -omM:                                           Copyright © by The CGRU team
 *    '          '
\* ....................................................................................................... */

#include "parserhost.h"

#include "../libafanasy/service.h"

#ifdef WINNT
//#define strcpy strcpy_s
#endif

#define AFOUTPUT
#undef AFOUTPUT
#include "../include/macrooutput.h"

const int ParserHost::ms_DataSizeMax   = 1 << 20; // 1 Mega Byte
const int ParserHost::ms_DataSizeHalf  = ParserHost::ms_DataSizeMax  >> 1; // A half of the maximum
const int ParserHost::ms_DataShiftMin = ParserHost::ms_DataSizeHalf >> 1; // A quater of the maximum

const char* ParserHost::ms_overload_string = "\n\
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

ParserHost::ParserHost( af::Service * i_service, LogWriter * i_log_writer):
	m_service( i_service),
	m_log_writer( i_log_writer),
	m_own_log_writer( false),
	m_percent( 0),
	m_frame( 0),
	m_percentframe( 0),
	m_progress_changed(false),
	m_error( false),
	m_fatalerror(false),
	m_warning( false),
	m_badresult( false),
	m_finishedsuccess( false)
{
	if (m_log_writer == nullptr)
	{
		m_log_writer = new MemoryLogWriter();
		m_own_log_writer = true;
	}
}

ParserHost::~ParserHost()
{
	if (m_own_log_writer && m_log_writer != nullptr)
		delete m_log_writer;
}

void ParserHost::read(const std::string & i_mode, int i_pid, std::string & io_output, const std::string & i_resources)
{
	parse(i_mode, i_pid, io_output, i_resources);

	// Post-Python execution: write the transformed/final output to the LogWriter backend
	if (m_log_writer != nullptr && io_output.size() > 0)
	{
		m_log_writer->write(io_output.data(), io_output.size());
	}
}

void ParserHost::parse(const std::string & i_mode, int i_pid, std::string & io_output, const std::string & i_resources)
{
	bool _warning         = false;
	bool _error           = false;
	bool _fatalerror      = false;
	bool _badresult       = false;
	bool _finishedsuccess = false;

	m_resources = i_resources;

	m_service->parse(i_mode, i_pid,
			io_output, m_resources,
			m_percent, m_frame, m_percentframe,
			m_activity, m_report,
			m_progress_changed,
			_warning, _error, _fatalerror, _badresult, _finishedsuccess);

	if ( _error           ) m_error           = true;
	if ( _fatalerror      ) m_fatalerror      = true;
	if ( _warning         ) m_warning         = true;
	if ( _badresult       ) m_badresult       = true;
	if ( _finishedsuccess ) m_finishedsuccess = true;
#ifdef AFOUTPUT
	printf("PERCENT: %d%%", m_percent);
	printf("; FRAME: %d", m_frame);
	printf("; PERCENTFRAME: %d%%", m_percentframe);
	if( _error           ) printf("; ERROR");
	if( _fatalerror      ) printf("; FATALERROR");
	if( _warning         ) printf("; WARNING");
	if( _badresult       ) printf("; BAD RESULT");
	if( _finishedsuccess ) printf("; FINISHED SUCCESS");
	printf("\n");
#endif
}
