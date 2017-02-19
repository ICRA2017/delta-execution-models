/**
 * Copyright 2017 by Alex Mitrevski <aleksandar.mitrevski@h-brs.de>
 *
 * This file is part of delta-execution-models.
 *
 * delta-execution-models is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * delta-execution-models is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with delta-execution-models. If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

#include <string>
#include <fstream>
#include <vector>
#include <cstdlib>
#include "Structs.h"
#include "Enums.h"
#include "Utils.h"
#include "SimulationActor.h"
#include "ObjectFactory.h"

using std::string;
using std::vector;
using std::to_string;
using std::stof;

class Scenario
{
public:
	Scenario(ScenarioConfig& scenarioConfig, const DisplayConfig& displayConfig, int copies);
	void UpdateScenario(const ScenarioConfig& scenarioConfig, const DisplayConfig& displayConfig);
	virtual void SaveLearningData(const string& file, const Tolerances& tolerances) const = 0;
	virtual void UpdateTrials(TrialData& trialData, const Tolerances& tolerances) = 0;
	bool TrialsCompleted(const TrialData& trialData) const;
	void SaveTrialData(const TrialData& trialData) const;

protected:
	struct Objects
	{
		ASimulationActor* manipObj;
		vector<ASimulationActor*> staticObj;
        vector<int> staticObjIdx;
	};

	void GetDeltaData(const Objects& objects, string& data, int idx) const;
	void GetDeltaNotData(const Objects& objects, string& data, int idx) const;
	virtual bool IsSuccessful(const Objects& objects, int idx, const Tolerances& tolerances) const = 0;

	RandomPoseGenerator poseGenerator;
	vector<ASimulationActor*> floors;
	vector<vector<ASimulationActor*>> objects;
	vector<vector<ASimulationActor*>> manipulatedObjects;
	vector<int> manipulatedObjectIdx;

	vector<vector<FVector>> initPositions;
	vector<vector<FRotator>> initRotations;
	vector<vector<FBox>> initBoundingBoxes;

private:
    void InitialiseTrials(ScenarioConfig& scenarioConfig, int copies);
	void CreateScenario(const ScenarioConfig& scenarioConfig, const DisplayConfig& displayConfig, int copies);
	void AddModel(int copyIdx, const ModelConfig& modelConfig, const DisplayConfig& displayConfig, int row, int column);
	void SetManipulatedObjectPose(int copyIdx, const ScenarioConfig& scenarioConfig, const DisplayConfig& displayConfig, int row, int column);
	Pose GenerateRandomPose();
	vector<Pose> GenerateOptimisedPoses(int copyIdx, const OptimisationParams& optimisationParams);
	void WriteOptimisationData(int copyIdx, const OptimisationParams& optimisationParams);
	void CallOptimisationScript(const string& scriptName);
	vector<Pose> ReadOptimisedData(const string& file);

	vector<vector<Pose>> poseCache;
	vector<int> poseCacheIdx;
	int copyCount;
};

typedef Scenario* ScenarioPtr;
