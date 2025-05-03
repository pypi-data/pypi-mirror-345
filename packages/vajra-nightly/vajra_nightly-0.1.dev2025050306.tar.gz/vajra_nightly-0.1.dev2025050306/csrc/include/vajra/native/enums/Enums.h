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
//==============================================================================
#include <zmq.hpp>
//==============================================================================
#include "commons/StdCommon.h"
//==============================================================================
namespace vajra {
//==============================================================================
enum class ReplicasetSchedulerType { PULL, ROUND_ROBIN };
//==============================================================================
enum class ReplicasetControllerType { LLM };
//==============================================================================
enum class ReplicaControllerType { LLM_BASE, LLM_PIPELINE_PARALLEL };
//==============================================================================
enum class ReplicaSchedulerType { FIXED_CHUNK, DYNAMIC_CHUNK, SPACE_SHARING };
//==============================================================================
enum class RequestPrioritizerType { FCFS, EDF, LRS };
//==============================================================================
enum class MetricsStoreType { ENGINE, WORKER };
//==============================================================================
enum class TransferBackendType { TORCH = 0 };
//==============================================================================
enum class TransferOperationRanksType { MATCHING = 0, ALL = 1, SINGLE = 2 };
//==============================================================================
enum class ZmqConstants {
  PUB = ZMQ_PUB,
  SUB = ZMQ_SUB,
  PUSH = ZMQ_PUSH,
  PULL = ZMQ_PULL,
  SUBSCRIBE = ZMQ_SUBSCRIBE
};
//==============================================================================
}  // namespace vajra
//==============================================================================
