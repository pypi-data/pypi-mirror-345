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
#include <Highs.h>
#include <gtest/gtest.h>

#include "commons/StdCommon.h"
#include "native/utils/ProtoUtils.h"

namespace vajra {
namespace {

class HighsTest : public ::testing::Test {
 protected:
  void SetUp() override {}
};

TEST_F(HighsTest, TestBasicILP) {
  // from
  // https://github.com/ERGO-Code/HiGHS/blob/master/examples/call_highs_from_cpp.cpp
  // Create and populate a HighsModel instance for the LP
  //
  // Min    f  =  x_0 +  x_1 + 3
  // s.t.                x_1 <= 7
  //        5 <=  x_0 + 2x_1 <= 15
  //        6 <= 3x_0 + 2x_1
  // 0 <= x_0 <= 4; 1 <= x_1
  //
  // Although the first constraint could be expressed as an upper
  // bound on x_1, it serves to illustrate a non-trivial packed
  // column-wise matrix.
  //
  HighsModel model;
  model.lp_.num_col_ = 2;
  model.lp_.num_row_ = 3;
  model.lp_.sense_ = ObjSense::kMinimize;
  model.lp_.offset_ = 3;
  model.lp_.col_cost_ = {1.0, 1.0};
  model.lp_.col_lower_ = {0.0, 1.0};
  model.lp_.col_upper_ = {4.0, 1.0e30};
  model.lp_.row_lower_ = {-1.0e30, 5.0, 6.0};
  model.lp_.row_upper_ = {7.0, 15.0, 1.0e30};
  //
  // Here the orientation of the matrix is column-wise
  model.lp_.a_matrix_.format_ = MatrixFormat::kColwise;
  // a_start_ has num_col_1 entries, and the last entry is the number
  // of nonzeros in A, allowing the number of nonzeros in the last
  // column to be defined
  model.lp_.a_matrix_.start_ = {0, 2, 5};
  model.lp_.a_matrix_.index_ = {1, 2, 0, 1, 2};
  model.lp_.a_matrix_.value_ = {1.0, 3.0, 1.0, 2.0, 2.0};
  //
  // Create a Highs instance
  Highs highs;
  HighsStatus return_status;
  //
  // Pass the model to HiGHS
  return_status = highs.passModel(model);
  EXPECT_EQ(return_status, HighsStatus::kOk);
  // If a user passes a model with entries in
  // model.lp_.a_matrix_.value_ less than (the option)
  // small_matrix_value in magnitude, they will be ignored. A logging
  // message will indicate this, and passModel will return
  // HighsStatus::kWarning
  //
  // Get a const reference to the LP data in HiGHS
  const HighsLp& lp = highs.getLp();
  //
  // Solve the model
  return_status = highs.run();
  EXPECT_EQ(return_status, HighsStatus::kOk);
  //
  // Get the model status
  const HighsModelStatus& model_status = highs.getModelStatus();
  EXPECT_EQ(model_status, HighsModelStatus::kOptimal);
  //
  // Get the solution information
  const HighsInfo& info = highs.getInfo();
  const bool has_values = info.primal_solution_status;
  const bool has_duals = info.dual_solution_status;
  const bool has_basis = info.basis_validity;
  //
  // Get the solution values and basis
  const HighsSolution& solution = highs.getSolution();
  const HighsBasis& basis = highs.getBasis();

  // Now indicate that all the variables must take integer values
  model.lp_.integrality_.resize(lp.num_col_);
  for (int col = 0; col < lp.num_col_; col++)
    model.lp_.integrality_[col] = HighsVarType::kInteger;

  highs.passModel(model);
  // Solve the model
  return_status = highs.run();
  EXPECT_EQ(return_status, HighsStatus::kOk);
}
}  // namespace
}  // namespace vajra
