//==============================================================================
// Copyright 2025 Vajra Team; Georgia Institute of Technology
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//==============================================================================
#pragma once

#include <optional>

#include "commons/Logging.h"
#include "commons/StdCommon.h"
#include "native/configs/ModelConfig.h"
//==============================================================================
namespace vajra {
//==============================================================================
// Output Response
//==============================================================================
struct OutputResponse final {
  OutputResponse(const std::string& request_id_param,
                 const std::string& text_param,
                 const std::vector<uint64_t>& token_ids_param,
                 const std::vector<uint64_t>& prompt_token_ids_param,
                 const std::string& finish_reason_param, bool finished_param,
                 bool is_delta_param, bool is_first_chunk_param)
      : request_id(request_id_param),
        text(text_param),
        token_ids(token_ids_param),
        prompt_token_ids(prompt_token_ids_param),
        finish_reason(finish_reason_param),
        finished(finished_param),
        is_delta(is_delta_param),
        is_first_chunk(is_first_chunk_param) {}

  OutputResponse(const OutputResponse& other)
      : request_id(other.request_id),
        text(other.text),
        token_ids(other.token_ids),
        prompt_token_ids(other.prompt_token_ids),
        finish_reason(other.finish_reason),
        finished(other.finished),
        is_delta(other.is_delta),
        is_first_chunk(other.is_first_chunk) {}

  OutputResponse(OutputResponse&& other) noexcept
      : request_id(std::move(other.request_id)),
        text(std::move(other.text)),
        token_ids(std::move(other.token_ids)),
        prompt_token_ids(std::move(other.prompt_token_ids)),
        finish_reason(std::move(other.finish_reason)),
        finished(other.finished),
        is_delta(other.is_delta),
        is_first_chunk(other.is_first_chunk) {}

  const std::string request_id;
  const std::string text;
  const std::vector<uint64_t> token_ids;
  const std::vector<uint64_t> prompt_token_ids;
  const std::string finish_reason;
  const bool finished;
  const bool is_delta;
  const bool is_first_chunk;
};

//==============================================================================
// Error Response
//==============================================================================
struct ErrorResponse final {
  ErrorResponse(const std::string& request_id_param,
                const std::string& error_message_param)
      : request_id(request_id_param), error_message(error_message_param) {}

  ErrorResponse(const ErrorResponse& other)
      : request_id(other.request_id), error_message(other.error_message) {}

  ErrorResponse(ErrorResponse&& other) noexcept
      : request_id(std::move(other.request_id)),
        error_message(std::move(other.error_message)) {}

  const std::string request_id;
  const std::string error_message;
};

//==============================================================================
// Startup Response
//==============================================================================
struct StartupResponse final {
  explicit StartupResponse(bool server_ready_param)
      : server_ready(server_ready_param) {}

  StartupResponse(const StartupResponse& other)
      : server_ready(other.server_ready) {}

  StartupResponse(StartupResponse&& other) noexcept
      : server_ready(other.server_ready) {}

  const bool server_ready;
};

//==============================================================================
// Remote Inference Response
//==============================================================================
struct RemoteInferenceResponse final {
  enum class Type { OUTPUT, ERROR, STARTUP, MODEL_CONFIG };

  // Constructor for OutputResponse
  explicit RemoteInferenceResponse(const OutputResponse& output_response_param)
      : type(Type::OUTPUT), output_response(output_response_param) {}

  // Constructor for ErrorResponse
  explicit RemoteInferenceResponse(const ErrorResponse& error_response_param)
      : type(Type::ERROR), error_response(error_response_param) {}

  // Constructor for StartupResponse
  explicit RemoteInferenceResponse(
      const StartupResponse& startup_response_param)
      : type(Type::STARTUP), startup_response(startup_response_param) {}

  // Constructor for ModelConfig
  explicit RemoteInferenceResponse(const ModelConfig& model_config_param)
      : type(Type::MODEL_CONFIG), model_config(model_config_param) {}

  RemoteInferenceResponse(const RemoteInferenceResponse& other)
      : type(other.type),
        output_response(other.output_response),
        error_response(other.error_response),
        startup_response(other.startup_response),
        model_config(other.model_config) {}

  RemoteInferenceResponse(RemoteInferenceResponse&& other) noexcept
      : type(other.type),
        output_response(std::move(other.output_response)),
        error_response(std::move(other.error_response)),
        startup_response(std::move(other.startup_response)),
        model_config(std::move(other.model_config)) {}

  const Type type;

  std::optional<OutputResponse> output_response;
  std::optional<ErrorResponse> error_response;
  std::optional<StartupResponse> startup_response;
  std::optional<ModelConfig> model_config;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
