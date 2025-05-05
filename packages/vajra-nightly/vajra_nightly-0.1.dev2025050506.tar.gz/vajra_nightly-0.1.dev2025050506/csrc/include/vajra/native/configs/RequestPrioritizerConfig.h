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

#include "commons/StdCommon.h"
#include "native/enums/Enums.h"
//==============================================================================
namespace vajra {
//==============================================================================
struct BaseRequestPrioritizerConfig {
  virtual ~BaseRequestPrioritizerConfig() = default;
  virtual RequestPrioritizerType GetType() const = 0;
};
//==============================================================================
struct FcfsRequestPrioritizerConfig final
    : public BaseRequestPrioritizerConfig {
  RequestPrioritizerType GetType() const override {
    return RequestPrioritizerType::FCFS;
  }
};
//==============================================================================
struct EdfRequestPrioritizerConfig : public BaseRequestPrioritizerConfig {
  EdfRequestPrioritizerConfig(float deadline_multiplier_param = 1.5,
                              float min_deadline_param = 0.5)
      : deadline_multiplier(deadline_multiplier_param),
        min_deadline(min_deadline_param) {}

  RequestPrioritizerType GetType() const override {
    return RequestPrioritizerType::EDF;
  }

  const float deadline_multiplier;
  const float min_deadline;
};
//==============================================================================
struct LrsRequestPrioritizerConfig final : public EdfRequestPrioritizerConfig {
  LrsRequestPrioritizerConfig(float deadline_multiplier_param = 1.5,
                              float min_deadline_param = 0.5)
      : EdfRequestPrioritizerConfig(deadline_multiplier_param,
                                    min_deadline_param) {}

  RequestPrioritizerType GetType() const override {
    return RequestPrioritizerType::LRS;
  }
};
//==============================================================================
}  // namespace vajra
//==============================================================================
