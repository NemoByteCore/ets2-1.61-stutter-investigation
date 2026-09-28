// NemoChainProbe161.cpp
// EXPERIMENTAL v0.1 — HOLD as a decisive runtime probe.
// The upper 140227140 -> 140226960 region and lower 141473E60 -> ... region
// are not yet proven to form one continuous direct-call chain.
// v0.1 telemetry also uses cumulative max and independently timed ~5 s rows.
// See docs/nemo-chain-probe-161.md before using this source.
// Exact-build chain profiler for ETS2 1.61.1.1 rev 6949e633e77902f7e023819d3131cc6ccce3707f
// EXE SHA256: EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53
// Fail-closed: PE timestamp + SizeOfImage + exact prologs for every hook.

#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static const DWORD EXPECTED_TIMESTAMP = 0x6AB3C451u;
static const DWORD EXPECTED_SIZE_IMAGE = 0x0398A000u;

static const uint64_t RVA_RG         = 0x00227140ull;
static const uint64_t RVA_T1         = 0x00226960ull;
static const uint64_t RVA_WINNER     = 0x01473E60ull;
static const uint64_t RVA_RQ_ONE     = 0x0160D010ull;
static const uint64_t RVA_HEAD       = 0x0160D580ull;
static const uint64_t RVA_DOWNSTREAM = 0x002E5FF0ull;
static const uint64_t RVA_BUNDLE     = 0x002E5040ull;
static const uint64_t RVA_DESCRIPTOR = 0x0029F9B0ull;

static const BYTE SIG_RG[16] = {
  0x48,0x89,0x54,0x24,0x10,0x48,0x89,0x4C,0x24,0x08,0x55,0x53,0x56,0x57,0x41,0x54
};
static const BYTE SIG_T1[15] = {
  0x48,0x89,0x5C,0x24,0x08,0x48,0x89,0x74,0x24,0x18,0x48,0x89,0x54,0x24,0x10
};
static const BYTE SIG_WINNER[14] = {
  0x48,0x8B,0xC4,0x57,0x48,0x81,0xEC,0xC0,0x00,0x00,0x00,0x48,0x8B,0xFA
};
static const BYTE SIG_RQ_ONE[17] = {
  0x4C,0x89,0x44,0x24,0x18,0x53,0x55,0x57,0x41,0x55,0x48,0x81,0xEC,0x18,0x01,0x00,0x00
};
static const BYTE SIG_HEAD[17] = {
  0x40,0x53,0x48,0x83,0xEC,0x40,0x4D,0x8B,0x58,0x40,0x48,0x8B,0xDA,0x49,0x8B,0x48,0x18
};
static const BYTE SIG_DOWNSTREAM[14] = {
  0x48,0x89,0x54,0x24,0x10,0x48,0x89,0x4C,0x24,0x08,0x55,0x53,0x56,0x57
};
static const BYTE SIG_BUNDLE[15] = {
  0x4C,0x8B,0xDC,0x4D,0x89,0x4B,0x20,0x4D,0x89,0x43,0x18,0x49,0x89,0x53,0x10
};
static const BYTE SIG_DESCRIPTOR[15] = {
  0x48,0x8B,0xC4,0x4C,0x89,0x48,0x20,0x4C,0x89,0x40,0x18,0x48,0x89,0x50,0x10
};

struct Hook {
  BYTE* target;
  DWORD len;
  BYTE original[32];
  BYTE* trampoline;
  bool installed;
};

struct alignas(8) Stat {
  volatile LONG64 calls;
  volatile LONG64 samples;
  volatile LONG64 ticks;
  volatile LONG64 max_ticks;
};

enum StatId {
  ST_RG=0, ST_T1, ST_WINNER, ST_RQ, ST_HEAD, ST_DOWN, ST_BUNDLE, ST_DESC, ST_COUNT
};

static Stat g_stats[ST_COUNT] = {};
static Hook g_hooks[ST_COUNT] = {};
static BYTE* g_exe = nullptr;
static HANDLE g_log = INVALID_HANDLE_VALUE;
static LARGE_INTEGER g_freq = {};
static LARGE_INTEGER g_start = {};
static volatile LONG64 g_last_report = 0;
static volatile LONG g_reporting = 0;

static const DWORD SAMPLE_MASK[ST_COUNT] = {
  0, 7, 15, 15, 15, 15, 63, 63
};

static void write_log(const char* s) {
  if (g_log == INVALID_HANDLE_VALUE) return;
  DWORD n=(DWORD)strlen(s), done=0;
  WriteFile(g_log,s,n,&done,nullptr);
}

static void make_abs_jmp(BYTE* out, void* dst) {
  out[0]=0xFF; out[1]=0x25; out[2]=0; out[3]=0; out[4]=0; out[5]=0;
  *(uint64_t*)(out+6)=(uint64_t)(uintptr_t)dst;
}

static bool install_hook(Hook& h, BYTE* target, DWORD len, void* replacement) {
  if (len < 14 || len > 32) return false;
  h.target=target; h.len=len; h.installed=false; h.trampoline=nullptr;
  memcpy(h.original,target,len);
  h.trampoline=(BYTE*)VirtualAlloc(nullptr,len+14,MEM_COMMIT|MEM_RESERVE,PAGE_EXECUTE_READWRITE);
  if (!h.trampoline) return false;
  memcpy(h.trampoline,target,len);
  make_abs_jmp(h.trampoline+len,target+len);
  FlushInstructionCache(GetCurrentProcess(),h.trampoline,len+14);

  DWORD old=0;
  if (!VirtualProtect(target,len,PAGE_EXECUTE_READWRITE,&old)) return false;
  BYTE patch[32]; memset(patch,0x90,sizeof(patch));
  make_abs_jmp(patch,replacement);
  memcpy(target,patch,len);
  DWORD ignored=0;
  VirtualProtect(target,len,old,&ignored);
  FlushInstructionCache(GetCurrentProcess(),target,len);
  h.installed=true;
  return true;
}

static void remove_hook(Hook& h) {
  if (h.installed) {
    DWORD old=0;
    if (VirtualProtect(h.target,h.len,PAGE_EXECUTE_READWRITE,&old)) {
      memcpy(h.target,h.original,h.len);
      DWORD ignored=0;
      VirtualProtect(h.target,h.len,old,&ignored);
      FlushInstructionCache(GetCurrentProcess(),h.target,h.len);
    }
    h.installed=false;
  }
  if (h.trampoline) {
    VirtualFree(h.trampoline,0,MEM_RELEASE);
    h.trampoline=nullptr;
  }
}

static void remove_all() {
  for (int i=ST_COUNT-1;i>=0;--i) remove_hook(g_hooks[i]);
}

static void atomic_max(volatile LONG64* p, LONG64 v) {
  LONG64 cur=InterlockedCompareExchange64(p,0,0);
  while (v>cur) {
    LONG64 old=InterlockedCompareExchange64(p,v,cur);
    if (old==cur) break;
    cur=old;
  }
}

static bool sample_begin(StatId id, LARGE_INTEGER& a) {
  LONG64 c=InterlockedIncrement64(&g_stats[id].calls);
  if ((c & SAMPLE_MASK[id]) != 0) return false;
  QueryPerformanceCounter(&a);
  return true;
}

static void sample_end(StatId id, const LARGE_INTEGER& a) {
  LARGE_INTEGER b; QueryPerformanceCounter(&b);
  LONG64 d=b.QuadPart-a.QuadPart;
  InterlockedIncrement64(&g_stats[id].samples);
  InterlockedExchangeAdd64(&g_stats[id].ticks,d);
  atomic_max(&g_stats[id].max_ticks,d);
}

static unsigned long long ticks_to_us(LONG64 t) {
  if (g_freq.QuadPart<=0) return 0;
  return (unsigned long long)((t*1000000ll)/g_freq.QuadPart);
}

static LONG64 atomic_read64(volatile LONG64* p) {
  return InterlockedCompareExchange64(p,0,0);
}

static void report_row(LONGLONG now) {
  char buf[4096];
  unsigned long long ms=(unsigned long long)(((now-g_start.QuadPart)*1000ll)/g_freq.QuadPart);
  int n=snprintf(buf,sizeof(buf),"%llu",ms);
  for (int i=0;i<ST_COUNT && n>0 && n<(int)sizeof(buf)-128;i++) {
    LONG64 calls=atomic_read64(&g_stats[i].calls);
    LONG64 samples=atomic_read64(&g_stats[i].samples);
    LONG64 ticks=atomic_read64(&g_stats[i].ticks);
    LONG64 maxv=atomic_read64(&g_stats[i].max_ticks);
    n += snprintf(buf+n,sizeof(buf)-n,",%lld,%lld,%llu,%llu",
      (long long)calls,(long long)samples,ticks_to_us(ticks),ticks_to_us(maxv));
  }
  if (n>0 && n<(int)sizeof(buf)-3) {
    buf[n++]='\r'; buf[n++]='\n'; buf[n]=0; write_log(buf);
  }
}

static void maybe_report() {
  LARGE_INTEGER now; QueryPerformanceCounter(&now);
  LONG64 last=atomic_read64(&g_last_report);
  if (now.QuadPart-last < g_freq.QuadPart*5) return;
  if (InterlockedCompareExchange(&g_reporting,1,0)!=0) return;
  last=atomic_read64(&g_last_report);
  if (now.QuadPart-last >= g_freq.QuadPart*5) {
    InterlockedExchange64(&g_last_report,now.QuadPart);
    report_row(now.QuadPart);
  }
  InterlockedExchange(&g_reporting,0);
}

using FnRG   = void(*)(uint64_t,int64_t);
using FnT1   = void(*)(uint64_t,uint64_t,void*,void*);
using FnWin  = void(*)(uint64_t,void*,uint64_t,int64_t);
using FnRQ   = void(*)(uint32_t,void*,int64_t);
using FnHead = void(*)(uint64_t,uint64_t,uint8_t*,uint64_t);
using FnDown = void(*)(uint64_t,int64_t,int64_t,int,uint64_t,int64_t);
using FnBund = void(*)(int64_t,int64_t*,int64_t,void*);
using FnDesc = void(*)(int64_t,int64_t,int64_t,int64_t,uint64_t);

extern "C" __declspec(noinline) void hook_rg(uint64_t a,int64_t b) {
  LARGE_INTEGER q; bool s=sample_begin(ST_RG,q);
  ((FnRG)g_hooks[ST_RG].trampoline)(a,b);
  if(s) sample_end(ST_RG,q);
  maybe_report();
}
extern "C" __declspec(noinline) void hook_t1(uint64_t a,uint64_t b,void* c,void* d) {
  LARGE_INTEGER q; bool s=sample_begin(ST_T1,q);
  ((FnT1)g_hooks[ST_T1].trampoline)(a,b,c,d);
  if(s) sample_end(ST_T1,q);
}
extern "C" __declspec(noinline) void hook_winner(uint64_t a,void* b,uint64_t c,int64_t d) {
  LARGE_INTEGER q; bool s=sample_begin(ST_WINNER,q);
  ((FnWin)g_hooks[ST_WINNER].trampoline)(a,b,c,d);
  if(s) sample_end(ST_WINNER,q);
}
extern "C" __declspec(noinline) void hook_rq(uint32_t a,void* b,int64_t c) {
  LARGE_INTEGER q; bool s=sample_begin(ST_RQ,q);
  ((FnRQ)g_hooks[ST_RQ].trampoline)(a,b,c);
  if(s) sample_end(ST_RQ,q);
}
extern "C" __declspec(noinline) void hook_head(uint64_t a,uint64_t b,uint8_t* c,uint64_t d) {
  LARGE_INTEGER q; bool s=sample_begin(ST_HEAD,q);
  ((FnHead)g_hooks[ST_HEAD].trampoline)(a,b,c,d);
  if(s) sample_end(ST_HEAD,q);
}
extern "C" __declspec(noinline) void hook_down(uint64_t a,int64_t b,int64_t c,int d,uint64_t e,int64_t f) {
  LARGE_INTEGER q; bool s=sample_begin(ST_DOWN,q);
  ((FnDown)g_hooks[ST_DOWN].trampoline)(a,b,c,d,e,f);
  if(s) sample_end(ST_DOWN,q);
}
extern "C" __declspec(noinline) void hook_bundle(int64_t a,int64_t* b,int64_t c,void* d) {
  LARGE_INTEGER q; bool s=sample_begin(ST_BUNDLE,q);
  ((FnBund)g_hooks[ST_BUNDLE].trampoline)(a,b,c,d);
  if(s) sample_end(ST_BUNDLE,q);
}
extern "C" __declspec(noinline) void hook_desc(int64_t a,int64_t b,int64_t c,int64_t d,uint64_t e) {
  LARGE_INTEGER q; bool s=sample_begin(ST_DESC,q);
  ((FnDesc)g_hooks[ST_DESC].trampoline)(a,b,c,d,e);
  if(s) sample_end(ST_DESC,q);
}

static bool sig_eq(uint64_t rva, const BYTE* sig, size_t n) {
  return memcmp(g_exe+rva,sig,n)==0;
}

static bool validate_build() {
  g_exe=(BYTE*)GetModuleHandleA(nullptr);
  if (!g_exe) return false;
  auto dos=(IMAGE_DOS_HEADER*)g_exe;
  if (dos->e_magic!=IMAGE_DOS_SIGNATURE) return false;
  auto nt=(IMAGE_NT_HEADERS64*)(g_exe+dos->e_lfanew);
  if (nt->Signature!=IMAGE_NT_SIGNATURE) return false;
  if (nt->FileHeader.TimeDateStamp!=EXPECTED_TIMESTAMP) return false;
  if (nt->OptionalHeader.SizeOfImage!=EXPECTED_SIZE_IMAGE) return false;
  if (!sig_eq(RVA_RG,SIG_RG,sizeof(SIG_RG))) return false;
  if (!sig_eq(RVA_T1,SIG_T1,sizeof(SIG_T1))) return false;
  if (!sig_eq(RVA_WINNER,SIG_WINNER,sizeof(SIG_WINNER))) return false;
  if (!sig_eq(RVA_RQ_ONE,SIG_RQ_ONE,sizeof(SIG_RQ_ONE))) return false;
  if (!sig_eq(RVA_HEAD,SIG_HEAD,sizeof(SIG_HEAD))) return false;
  if (!sig_eq(RVA_DOWNSTREAM,SIG_DOWNSTREAM,sizeof(SIG_DOWNSTREAM))) return false;
  if (!sig_eq(RVA_BUNDLE,SIG_BUNDLE,sizeof(SIG_BUNDLE))) return false;
  if (!sig_eq(RVA_DESCRIPTOR,SIG_DESCRIPTOR,sizeof(SIG_DESCRIPTOR))) return false;
  return true;
}

static bool open_log() {
  char path[MAX_PATH];
  DWORD n=GetModuleFileNameA(nullptr,path,MAX_PATH);
  if (!n || n>=MAX_PATH) return false;
  int slash=-1;
  for (DWORD i=0;i<n;i++) if(path[i]=='\\' || path[i]=='/') slash=(int)i;
  if (slash<0) return false;
  const char* tail="plugins\\NemoChainProbe161.csv";
  snprintf(path+slash+1,MAX_PATH-(slash+1),"%s",tail);
  g_log=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,nullptr,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
  if (g_log==INVALID_HANDLE_VALUE) return false;
  write_log("# NemoChainProbe161 v0.1\r\n");
  write_log("# ETS2=1.61.1.1 rev=6949e633e77902f7e023819d3131cc6ccce3707f\r\n");
  write_log("# exe_sha256=EB17944139BE4DE3D70D0CD57CDAA7C52C9E326ECF2D0DD3EA2F806545C74A53\r\n");
  write_log("# fail_closed=PE_timestamp+SizeOfImage+8_exact_prologs\r\n");
  write_log("# sample_div=rg:1,t1:8,winner:16,rq_one:16,head:16,downstream:16,bundle:64,descriptor:64\r\n");
  write_log("# values are cumulative; sample_us is cumulative sampled time, not scaled estimate\r\n");
  write_log("ms,rg_calls,rg_samples,rg_sample_us,rg_max_us,t1_calls,t1_samples,t1_sample_us,t1_max_us,winner_calls,winner_samples,winner_sample_us,winner_max_us,rq_one_calls,rq_one_samples,rq_one_sample_us,rq_one_max_us,head_calls,head_samples,head_sample_us,head_max_us,downstream_calls,downstream_samples,downstream_sample_us,downstream_max_us,bundle_calls,bundle_samples,bundle_sample_us,bundle_max_us,descriptor_calls,descriptor_samples,descriptor_sample_us,descriptor_max_us\r\n");
  return true;
}

static bool install_all() {
  if (!install_hook(g_hooks[ST_RG],g_exe+RVA_RG,16,(void*)&hook_rg)) return false;
  if (!install_hook(g_hooks[ST_T1],g_exe+RVA_T1,15,(void*)&hook_t1)) return false;
  if (!install_hook(g_hooks[ST_WINNER],g_exe+RVA_WINNER,14,(void*)&hook_winner)) return false;
  if (!install_hook(g_hooks[ST_RQ],g_exe+RVA_RQ_ONE,17,(void*)&hook_rq)) return false;
  if (!install_hook(g_hooks[ST_HEAD],g_exe+RVA_HEAD,17,(void*)&hook_head)) return false;
  if (!install_hook(g_hooks[ST_DOWN],g_exe+RVA_DOWNSTREAM,14,(void*)&hook_down)) return false;
  if (!install_hook(g_hooks[ST_BUNDLE],g_exe+RVA_BUNDLE,15,(void*)&hook_bundle)) return false;
  if (!install_hook(g_hooks[ST_DESC],g_exe+RVA_DESCRIPTOR,15,(void*)&hook_desc)) return false;
  return true;
}

extern "C" __declspec(dllexport) uint32_t scs_telemetry_init(uint32_t version,const void* params) {
  (void)version; (void)params;
  if (!open_log()) return 1;
  if (!validate_build()) {
    write_log("# FAIL exact build/signature validation; no hooks installed\r\n");
    CloseHandle(g_log); g_log=INVALID_HANDLE_VALUE; return 1;
  }
  if (!QueryPerformanceFrequency(&g_freq) || !QueryPerformanceCounter(&g_start) || g_freq.QuadPart<=0) {
    write_log("# FAIL QPC init\r\n"); CloseHandle(g_log); g_log=INVALID_HANDLE_VALUE; return 1;
  }
  InterlockedExchange64(&g_last_report,g_start.QuadPart);
  if (!install_all()) {
    write_log("# FAIL hook install; restoring installed hooks\r\n");
    remove_all(); CloseHandle(g_log); g_log=INVALID_HANDLE_VALUE; return 1;
  }
  write_log("# READY hooks=rg,t1,winner,rq_one,head,downstream,bundle,descriptor\r\n");
  return 0;
}

extern "C" __declspec(dllexport) void scs_telemetry_shutdown() {
  remove_all();
  if (g_log!=INVALID_HANDLE_VALUE) {
    write_log("# SHUTDOWN\r\n");
    CloseHandle(g_log); g_log=INVALID_HANDLE_VALUE;
  }
}

BOOL WINAPI DllMain(HINSTANCE,DWORD,LPVOID) { return TRUE; }
