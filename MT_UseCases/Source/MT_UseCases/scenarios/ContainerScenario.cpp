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

#include "MT_UseCases.h"
#include "ContainerScenario.h"

ContainerScenario::ContainerScenario(ScenarioConfig& scenarioConfig, const DisplayConfig& displayConfig, int copies)
	: Scenario(scenarioConfig, displayConfig, copies)
{ }

void ContainerScenario::SaveLearningData(const string& file, const Tolerances& tolerances) const
{
	string data = "";
	for (unsigned int i = 0; i<this->objects.size(); i++)
	{
		Objects objects;
		objects.manipObj = this->objects[i][1];
		objects.staticObj.push_back(this->objects[i][2]);
		objects.staticObj.push_back(this->objects[i][3]);
		objects.staticObjIdx.push_back(2);
		objects.staticObjIdx.push_back(3);

		this->GetDeltaData(objects, data, i);
		bool success = this->IsSuccessful(objects, i, tolerances);

		if (success)
			data += "1";
		else
			data += "0";
		data += "\n";
	}

	std::ofstream fileStream;
	fileStream.open(file, std::ios::app);
	fileStream << data;
	fileStream.close();
}

bool ContainerScenario::IsSuccessful(const Objects& objects, int idx, const Tolerances& tolerances) const
{
	FVector initStatic1Pos = this->initPositions[idx][objects.staticObjIdx[0]];
	FRotator initStatic1Rot = this->initRotations[idx][objects.staticObjIdx[0]];

	FVector initStatic2Pos = this->initPositions[idx][objects.staticObjIdx[1]];
	FRotator initStatic2Rot = this->initRotations[idx][objects.staticObjIdx[1]];

	const FBox& finalManipBox = objects.manipObj->GetComponentsBoundingBox(false);

	Pose finalStatic1Pose = objects.staticObj[0]->GetPose();
	const FBox& finalStatic1Box = objects.staticObj[0]->GetComponentsBoundingBox(false);

	Pose finalStatic2Pose = objects.staticObj[1]->GetPose();
	const FBox& finalStatic2Box = objects.staticObj[1]->GetComponentsBoundingBox(false);

	bool manipInside = abs(finalManipBox.Min.Z - finalStatic2Box.Min.Z) < tolerances.translationTolerance;
	bool movingBetweenStatic = IsBetween(finalManipBox, finalStatic1Box, finalStatic2Box, tolerances.translationTolerance);
	bool static1SamePose = IsPoseSame(Pose(initStatic1Pos, initStatic1Rot), finalStatic1Pose, tolerances.translationTolerance);
	bool static2SamePose = IsPoseSame(Pose(initStatic2Pos, initStatic2Rot), finalStatic2Pose, tolerances.translationTolerance);

	return (manipInside && static1SamePose && static2SamePose && movingBetweenStatic);
}

void ContainerScenario::UpdateTrials(TrialData& trialData, const Tolerances& tolerances)
{
	for (unsigned int i = 0; i<this->objects.size(); i++)
	{
		if (trialData.copyToTrialMap[i] >= trialData.numberOfTrials)
			continue;

		Objects objects;
		objects.manipObj = this->objects[i][1];
		objects.staticObj.push_back(NULL);
		objects.staticObj.push_back(NULL);
		objects.staticObjIdx.push_back(-1);
		objects.staticObjIdx.push_back(-1);

		bool success = false;
		for (int j = 2; j < this->objects[i].size(); j++)
		{
			if (success)
				break;

			for (int k = j + 1; k < this->objects[i].size(); k++)
			{
				if (success)
					break;

				objects.staticObj[0] = this->objects[i][j];
				objects.staticObj[1] = this->objects[i][k];
				objects.staticObjIdx[0] = j;
				objects.staticObjIdx[1] = k;

				success = this->IsSuccessful(objects, i, tolerances);
			}
		}

		if (success)
		{
			string message = "Trial " + std::to_string(trialData.copyToTrialMap[i]) + " finished with success";
			GEngine->AddOnScreenDebugMessage(-1, 2, FColor(255, 0, 0), FString(message.c_str()));
			trialData.trialSuccess[trialData.copyToTrialMap[i]] = true;
			trialData.trialCompleted[trialData.copyToTrialMap[i]] = true;
			trialData.copyToTrialMap[i] = trialData.trialCounter;
			trialData.trialCounter += 1;
		}
		else
		{
			if (trialData.attemptCounters[trialData.copyToTrialMap[i]] < trialData.attemptsPerTrial)
			{
				trialData.attemptCounters[trialData.copyToTrialMap[i]] += 1;
			}
			else
			{
				string message = "Trial " + std::to_string(trialData.copyToTrialMap[i]) + " finished with failure";
				GEngine->AddOnScreenDebugMessage(-1, 2, FColor(255, 0, 0), FString(message.c_str()));
				trialData.trialCompleted[trialData.copyToTrialMap[i]] = true;
				trialData.copyToTrialMap[i] = trialData.trialCounter;
				trialData.trialCounter += 1;
			}
		}
	}
}
