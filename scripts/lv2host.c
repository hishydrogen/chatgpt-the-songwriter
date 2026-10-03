/* lv2host: run one LV2 audio effect over a sound file, offline.
 *
 *   lv2host <plugin-uri> <in.wav> <out.wav> [symbol=value ...]
 *
 * Unlike lv2apply it supports what guitar amp plugins (guitarix gx_amp, gx_cabinet ...)
 * need: atom ports (left empty), urid:map, a synchronous worker (worker:schedule) and
 * bounded block length options. Reported latency is compensated (output trimmed).
 * Output is 32-bit float with the plugin's audio output count (mono in -> stereo plugin
 * input: the channel is duplicated; more file channels than inputs: extra ones dropped).
 *
 * Build (scripts/setup.sh does this):
 *   gcc -O2 -o /usr/local/bin/lv2host scripts/lv2host.c $(pkg-config --cflags --libs lilv-0 sndfile)
 */
#include <lilv/lilv.h>
#include <lv2/atom/atom.h>
#include <lv2/buf-size/buf-size.h>
#include <lv2/core/lv2.h>
#include <lv2/options/options.h>
#include <lv2/urid/urid.h>
#include <lv2/worker/worker.h>
#include <sndfile.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BLOCK 512
#define ATOM_CAP 65536
#define MAX_URIS 1024

static char *uris[MAX_URIS];
static int n_uris = 0;

static LV2_URID map_uri(LV2_URID_Map_Handle h, const char *uri) {
  (void)h;
  for (int i = 0; i < n_uris; i++)
    if (!strcmp(uris[i], uri)) return (LV2_URID)(i + 1);
  if (n_uris >= MAX_URIS) return 0;
  uris[n_uris] = strdup(uri);
  return (LV2_URID)(++n_uris);
}

static const char *unmap_uri(LV2_URID_Unmap_Handle h, LV2_URID id) {
  (void)h;
  return (id > 0 && (int)id <= n_uris) ? uris[id - 1] : NULL;
}

/* -- synchronous worker ---------------------------------------------------------- */
typedef struct {
  const LV2_Worker_Interface *iface;
  LV2_Handle handle;
  uint32_t resp_size[64];
  void *resp_data[64];
  int n_resp;
} Worker;
static Worker worker;

static LV2_Worker_Status respond(LV2_Worker_Respond_Handle h, uint32_t size, const void *data) {
  Worker *w = (Worker *)h;
  if (w->n_resp >= 64) return LV2_WORKER_ERR_NO_SPACE;
  w->resp_data[w->n_resp] = malloc(size);
  memcpy(w->resp_data[w->n_resp], data, size);
  w->resp_size[w->n_resp++] = size;
  return LV2_WORKER_SUCCESS;
}

static LV2_Worker_Status schedule(LV2_Worker_Schedule_Handle h, uint32_t size, const void *data) {
  Worker *w = (Worker *)h;
  if (!w->iface) return LV2_WORKER_ERR_UNKNOWN;
  return w->iface->work(w->handle, respond, w, size, data);
}

static void deliver_responses(void) {
  for (int i = 0; i < worker.n_resp; i++) {
    worker.iface->work_response(worker.handle, worker.resp_size[i], worker.resp_data[i]);
    free(worker.resp_data[i]);
  }
  worker.n_resp = 0;
  if (worker.iface && worker.iface->end_run) worker.iface->end_run(worker.handle);
}

int main(int argc, char **argv) {
  if (argc < 4) {
    fprintf(stderr, "usage: %s <plugin-uri> <in.wav> <out.wav> [symbol=value ...]\n", argv[0]);
    return 2;
  }
  LilvWorld *world = lilv_world_new();
  lilv_world_load_all(world);
  LilvNode *uri = lilv_new_uri(world, argv[1]);
  const LilvPlugin *plugin = lilv_plugins_get_by_uri(lilv_world_get_all_plugins(world), uri);
  if (!plugin) { fprintf(stderr, "plugin not found: %s\n", argv[1]); return 1; }

  SF_INFO in_info = {0};
  SNDFILE *in = sf_open(argv[2], SFM_READ, &in_info);
  if (!in) { fprintf(stderr, "cannot read %s\n", argv[2]); return 1; }
  double sr = in_info.samplerate;

  /* features */
  LV2_URID_Map map = {NULL, map_uri};
  LV2_URID_Unmap unmap = {NULL, unmap_uri};
  LV2_Feature map_f = {LV2_URID__map, &map};
  LV2_Feature unmap_f = {LV2_URID__unmap, &unmap};
  LV2_Worker_Schedule sched = {&worker, schedule};
  LV2_Feature sched_f = {LV2_WORKER__schedule, &sched};
  int32_t blk = BLOCK, minblk = 1;
  float srf = (float)sr;
  LV2_URID t_int = map_uri(NULL, LV2_ATOM__Int), t_float = map_uri(NULL, LV2_ATOM__Float);
  LV2_Options_Option opts[] = {
    {LV2_OPTIONS_INSTANCE, 0, map_uri(NULL, LV2_BUF_SIZE__maxBlockLength), sizeof(int32_t), t_int, &blk},
    {LV2_OPTIONS_INSTANCE, 0, map_uri(NULL, LV2_BUF_SIZE__minBlockLength), sizeof(int32_t), t_int, &minblk},
    {LV2_OPTIONS_INSTANCE, 0, map_uri(NULL, LV2_BUF_SIZE__nominalBlockLength), sizeof(int32_t), t_int, &blk},
    {LV2_OPTIONS_INSTANCE, 0, map_uri(NULL, "http://lv2plug.in/ns/ext/parameters#sampleRate"), sizeof(float), t_float, &srf},
    {LV2_OPTIONS_INSTANCE, 0, 0, 0, 0, NULL}};
  LV2_Feature opts_f = {LV2_OPTIONS__options, opts};
  LV2_Feature bounded_f = {LV2_BUF_SIZE__boundedBlockLength, NULL};
  LV2_Feature fixed_f = {LV2_BUF_SIZE__fixedBlockLength, NULL};
  const LV2_Feature *features[] = {&map_f, &unmap_f, &sched_f, &opts_f, &bounded_f, &fixed_f, NULL};

  LilvInstance *inst = lilv_plugin_instantiate(plugin, sr, features);
  if (!inst) { fprintf(stderr, "instantiate failed\n"); return 1; }
  const LV2_Worker_Interface *wi =
      (const LV2_Worker_Interface *)lilv_instance_get_extension_data(inst, LV2_WORKER__interface);
  worker.iface = wi;
  worker.handle = lilv_instance_get_handle(inst);

  LilvNode *audio_c = lilv_new_uri(world, LV2_CORE__AudioPort);
  LilvNode *control_c = lilv_new_uri(world, LV2_CORE__ControlPort);
  LilvNode *atom_c = lilv_new_uri(world, LV2_ATOM__AtomPort);
  LilvNode *input_c = lilv_new_uri(world, LV2_CORE__InputPort);
  LilvNode *latency_d = lilv_new_uri(world, LV2_CORE__latency);
  LilvNode *reports_p = lilv_new_uri(world, LV2_CORE__reportsLatency);

  uint32_t n_ports = lilv_plugin_get_num_ports(plugin);
  float *ctl = calloc(n_ports, sizeof(float));
  float *mins = calloc(n_ports, sizeof(float)), *maxs = calloc(n_ports, sizeof(float));
  float *defs = calloc(n_ports, sizeof(float));
  lilv_plugin_get_port_ranges_float(plugin, mins, maxs, defs);
  int ain[8], aout[8], n_ain = 0, n_aout = 0, latency_port = -1;
  float *abuf[16];
  int n_abuf = 0;
  void *atom_bufs[8];
  int atom_out[8], n_atom = 0;

  for (uint32_t i = 0; i < n_ports; i++) {
    const LilvPort *p = lilv_plugin_get_port_by_index(plugin, i);
    int is_in = lilv_port_is_a(plugin, p, input_c);
    if (lilv_port_is_a(plugin, p, audio_c)) {
      float *b = calloc(BLOCK, sizeof(float));
      abuf[n_abuf++] = b;
      lilv_instance_connect_port(inst, i, b);
      if (is_in && n_ain < 8) ain[n_ain++] = n_abuf - 1;
      else if (!is_in && n_aout < 8) aout[n_aout++] = n_abuf - 1;
    } else if (lilv_port_is_a(plugin, p, control_c)) {
      ctl[i] = isnan(defs[i]) ? 0.0f : defs[i];
      if (!is_in && lilv_port_has_property(plugin, p, reports_p)) latency_port = (int)i;
      if (!is_in) {
        LilvNodes *des = lilv_port_get_value(plugin, p, lilv_new_uri(world, LV2_CORE__designation));
        if (des) {
          LILV_FOREACH(nodes, it, des)
            if (lilv_node_equals(lilv_nodes_get(des, it), latency_d)) latency_port = (int)i;
          lilv_nodes_free(des);
        }
      }
      lilv_instance_connect_port(inst, i, &ctl[i]);
    } else if (lilv_port_is_a(plugin, p, atom_c)) {
      LV2_Atom_Sequence *seq = calloc(1, ATOM_CAP);
      atom_bufs[n_atom] = seq;
      atom_out[n_atom] = !is_in;
      if (is_in) {
        seq->atom.size = sizeof(LV2_Atom_Sequence_Body);
        seq->atom.type = map_uri(NULL, LV2_ATOM__Sequence);
      }
      n_atom++;
      lilv_instance_connect_port(inst, i, seq);
    } else {
      lilv_instance_connect_port(inst, i, NULL);
    }
  }

  /* control values from the command line: symbol=value */
  for (int a = 4; a < argc; a++) {
    char *eq = strchr(argv[a], '=');
    if (!eq) { fprintf(stderr, "bad control %s\n", argv[a]); return 1; }
    *eq = 0;
    LilvNode *sym = lilv_new_string(world, argv[a]);
    const LilvPort *p = lilv_plugin_get_port_by_symbol(plugin, sym);
    if (!p) { fprintf(stderr, "no port %s\n", argv[a]); return 1; }
    uint32_t idx = lilv_port_get_index(plugin, p);
    ctl[idx] = (float)atof(eq + 1);
    lilv_node_free(sym);
  }

  SF_INFO out_info = {0};
  out_info.samplerate = in_info.samplerate;
  out_info.channels = n_aout;
  out_info.format = SF_FORMAT_WAV | SF_FORMAT_FLOAT;
  SNDFILE *out = sf_open(argv[3], SFM_WRITE, &out_info);
  if (!out) { fprintf(stderr, "cannot write %s\n", argv[3]); return 1; }

  lilv_instance_activate(inst);
  /* settle: one silent block lets workers (cabinet IR loading) finish before audio */
  for (int warm = 0; warm < 8; warm++) {
    for (int c = 0; c < n_ain; c++) memset(abuf[ain[c]], 0, BLOCK * sizeof(float));
    for (int k = 0; k < n_atom; k++)
      if (atom_out[k]) ((LV2_Atom *)atom_bufs[k])->size = ATOM_CAP - sizeof(LV2_Atom);
    lilv_instance_run(inst, BLOCK);
    deliver_responses();
  }

  int ich = in_info.channels;
  float *ibuf = malloc(sizeof(float) * BLOCK * ich);
  float *obuf = malloc(sizeof(float) * BLOCK * (n_aout ? n_aout : 1));
  sf_count_t total = in_info.frames, done = 0, written = 0;
  long latency = -1;
  sf_count_t tail = (sf_count_t)sr;  /* flush one second of zeros after the input */
  while (written < total) {
    sf_count_t got = (done < total) ? sf_readf_float(in, ibuf, BLOCK) : 0;
    if (got < BLOCK) memset(ibuf + got * ich, 0, (BLOCK - got) * ich * sizeof(float));
    done += got;
    for (int c = 0; c < n_ain; c++) {
      int src = c < ich ? c : ich - 1;
      for (int s = 0; s < BLOCK; s++) abuf[ain[c]][s] = ibuf[s * ich + src];
    }
    for (int k = 0; k < n_atom; k++)
      if (atom_out[k]) ((LV2_Atom *)atom_bufs[k])->size = ATOM_CAP - sizeof(LV2_Atom);
    lilv_instance_run(inst, BLOCK);
    deliver_responses();
    if (latency < 0) latency = latency_port >= 0 ? (long)(ctl[latency_port] + 0.5f) : 0;
    int start = 0;
    if (latency > 0) {  /* drop the first `latency` output samples */
      long skip = latency < BLOCK ? latency : BLOCK;
      start = (int)skip;
      latency -= skip;
      if (latency == 0) latency = -2; /* done trimming */
    }
    int n = BLOCK - start;
    if (written + n > total) n = (int)(total - written);
    for (int s = 0; s < n; s++)
      for (int c = 0; c < n_aout; c++) obuf[s * n_aout + c] = abuf[aout[c]][start + s];
    if (n > 0) { sf_writef_float(out, obuf, n); written += n; }
    if (latency == -2) latency = 0;
    if (done >= total && tail-- <= 0) break;
  }
  sf_close(out);
  sf_close(in);
  lilv_instance_deactivate(inst);
  lilv_instance_free(inst);
  return 0;
}
