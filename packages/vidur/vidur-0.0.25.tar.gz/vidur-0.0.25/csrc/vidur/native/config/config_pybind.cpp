#include "vidur/config/config_pybind.h"

#include <pybind11/stl.h>

#include "vidur/config/config.h"

namespace vidur
{
namespace config
{
namespace py = pybind11;

void InitExecutionTimePredictorConfig(pybind11::module_& m)
{
  py::class_<ExecutionTimePredictorConfig>(m, "ExecutionTimePredictorConfig")
      .def(
          py::init<
              std::size_t,
              std::size_t,
              std::size_t,
              std::size_t,
              double,
              double,
              double,
              bool,
              bool,
              std::string>(),
          py::arg("kv_cache_prediction_granularity") = 256,
          py::arg("prediction_max_prefill_chunk_size") = 4096,
          py::arg("prediction_max_batch_size") = 128,
          py::arg("prediction_max_tokens_per_request") = 2 * 1024 * 1024,
          py::arg("attention_decode_batching_overhead_fraction") = 0.1,
          py::arg("nccl_cpu_launch_overhead_ms") = 0.02,
          py::arg("nccl_cpu_skew_overhead_per_device_ms") = 0.0,
          py::arg("use_native_execution_time_predictor") = true,
          py::arg("disable_kvp_communication") = true,
          py::arg("cache_dir") = ".vidur_cache")
      .def_readonly(
          "kv_cache_prediction_granularity",
          &ExecutionTimePredictorConfig::kv_cache_prediction_granularity)
      .def_readonly(
          "prediction_max_prefill_chunk_size",
          &ExecutionTimePredictorConfig::prediction_max_prefill_chunk_size)
      .def_readonly(
          "prediction_max_batch_size",
          &ExecutionTimePredictorConfig::prediction_max_batch_size)
      .def_readonly(
          "prediction_max_tokens_per_request",
          &ExecutionTimePredictorConfig::prediction_max_tokens_per_request)
      .def_readonly(
          "attention_decode_batching_overhead_fraction",
          &ExecutionTimePredictorConfig::
              attention_decode_batching_overhead_fraction)
      .def_readonly(
          "nccl_cpu_launch_overhead_ms",
          &ExecutionTimePredictorConfig::nccl_cpu_launch_overhead_ms)
      .def_readonly(
          "nccl_cpu_skew_overhead_per_device_ms",
          &ExecutionTimePredictorConfig::nccl_cpu_skew_overhead_per_device_ms)
      .def_readonly(
          "use_native_execution_time_predictor",
          &ExecutionTimePredictorConfig::use_native_execution_time_predictor)
      .def_readonly(
          "disable_kvp_communication",
          &ExecutionTimePredictorConfig::disable_kvp_communication)
      .def_readonly("cache_dir", &ExecutionTimePredictorConfig::cache_dir);
}

void InitReplicaConfig(pybind11::module_& m)
{
  py::class_<ReplicaConfig>(m, "ReplicaConfig")
      .def(
          py::init<std::size_t, std::size_t, std::size_t>(),
          py::arg("num_pipeline_stages"),
          py::arg("tensor_parallel_size"),
          py::arg("kv_parallel_size"))
      .def_readonly("num_pipeline_stages", &ReplicaConfig::num_pipeline_stages)
      .def_readonly(
          "tensor_parallel_size",
          &ReplicaConfig::tensor_parallel_size)
      .def_readonly("kv_parallel_size", &ReplicaConfig::kv_parallel_size);
}

void InitModelConfig(pybind11::module_& m)
{
  py::class_<ModelConfig>(m, "ModelConfig")
      .def(
          py::init<
              std::size_t,
              std::size_t,
              std::size_t,
              std::size_t,
              std::size_t,
              std::size_t,
              bool,
              bool,
              bool,
              bool,
              std::size_t>(),
          py::arg("num_layers"),
          py::arg("num_q_heads"),
          py::arg("num_kv_heads"),
          py::arg("embedding_dim"),
          py::arg("mlp_hidden_dim"),
          py::arg("max_model_len"),
          py::arg("use_gated_mlp"),
          py::arg("use_bias"),
          py::arg("use_qkv_bias"),
          py::arg("post_attn_norm"),
          py::arg("vocab_size"))
      .def_readonly("num_layers", &ModelConfig::num_layers)
      .def_readonly("num_q_heads", &ModelConfig::num_q_heads)
      .def_readonly("num_kv_heads", &ModelConfig::num_kv_heads)
      .def_readonly("embedding_dim", &ModelConfig::embedding_dim)
      .def_readonly("mlp_hidden_dim", &ModelConfig::mlp_hidden_dim)
      .def_readonly("max_model_len", &ModelConfig::max_model_len)
      .def_readonly("use_gated_mlp", &ModelConfig::use_gated_mlp)
      .def_readonly("use_bias", &ModelConfig::use_bias)
      .def_readonly("use_qkv_bias", &ModelConfig::use_qkv_bias)
      .def_readonly("post_attn_norm", &ModelConfig::post_attn_norm)
      .def_readonly("vocab_size", &ModelConfig::vocab_size);
}

} // namespace config
} // namespace vidur
