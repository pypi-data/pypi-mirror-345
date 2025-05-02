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
#include "native/datatypes/SamplingParams.h"
//==============================================================================
namespace vajra {
//==============================================================================
// Process Request
//==============================================================================
struct ProcessRequest final {
  ProcessRequest(const std::string& request_id_param,
                 const std::string& prompt_param,
                 const SamplingParams& sampling_params_param)
      : request_id(request_id_param),
        prompt(prompt_param),
        sampling_params(sampling_params_param) {}

  ProcessRequest(const ProcessRequest& other)
      : request_id(other.request_id),
        prompt(other.prompt),
        sampling_params(other.sampling_params) {}

  ProcessRequest(ProcessRequest&& other) noexcept
      : request_id(std::move(other.request_id)),
        prompt(std::move(other.prompt)),
        sampling_params(std::move(other.sampling_params)) {}

  const std::string request_id;
  const std::string prompt;
  const SamplingParams sampling_params;
};

//==============================================================================
// Abort Request
//==============================================================================
struct AbortRequest final {
  explicit AbortRequest(const std::string& request_id_param)
      : request_id(request_id_param) {}

  AbortRequest(const AbortRequest& other) : request_id(other.request_id) {}

  AbortRequest(AbortRequest&& other) noexcept
      : request_id(std::move(other.request_id)) {}

  const std::string request_id;
};

//==============================================================================
// Startup Request
//==============================================================================
struct StartupRequest final {
  explicit StartupRequest(bool client_ready_param)
      : client_ready(client_ready_param) {}

  StartupRequest(const StartupRequest& other)
      : client_ready(other.client_ready) {}

  StartupRequest(StartupRequest&& other) noexcept
      : client_ready(other.client_ready) {}

  const bool client_ready;
};

//==============================================================================
// Config Request
//==============================================================================
struct ConfigRequest final {
  explicit ConfigRequest(const std::string& request_id_param)
      : request_id(request_id_param) {}

  ConfigRequest(const ConfigRequest& other) : request_id(other.request_id) {}

  ConfigRequest(ConfigRequest&& other) noexcept
      : request_id(std::move(other.request_id)) {}

  const std::string request_id;
};

//==============================================================================
// Remote Inference Request
//==============================================================================
struct RemoteInferenceRequest final {
  enum class Type { PROCESS, ABORT, STARTUP, CONFIG };

  // Constructor for ProcessRequest
  explicit RemoteInferenceRequest(const ProcessRequest& process_request_param)
      : type(Type::PROCESS), process_request(process_request_param) {}

  // Constructor for AbortRequest
  explicit RemoteInferenceRequest(const AbortRequest& abort_request_param)
      : type(Type::ABORT), abort_request(abort_request_param) {}

  // Constructor for StartupRequest
  explicit RemoteInferenceRequest(const StartupRequest& startup_request_param)
      : type(Type::STARTUP), startup_request(startup_request_param) {}

  // Constructor for ConfigRequest
  explicit RemoteInferenceRequest(const ConfigRequest& config_request_param)
      : type(Type::CONFIG), config_request(config_request_param) {}

  RemoteInferenceRequest(const RemoteInferenceRequest& other)
      : type(other.type),
        process_request(other.process_request),
        abort_request(other.abort_request),
        startup_request(other.startup_request),
        config_request(other.config_request) {}

  RemoteInferenceRequest(RemoteInferenceRequest&& other) noexcept
      : type(other.type),
        process_request(std::move(other.process_request)),
        abort_request(std::move(other.abort_request)),
        startup_request(std::move(other.startup_request)),
        config_request(std::move(other.config_request)) {}

  const Type type;

  std::optional<ProcessRequest> process_request;
  std::optional<AbortRequest> abort_request;
  std::optional<StartupRequest> startup_request;
  std::optional<ConfigRequest> config_request;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
