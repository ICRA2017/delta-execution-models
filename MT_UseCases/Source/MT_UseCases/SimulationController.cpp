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
#include "SimulationController.h"

ASimulationController::ASimulationController(const FObjectInitializer& objectInitialiser)
	: Super(objectInitialiser)
{
	PrimaryActorTick.bCanEverTick = true;
}

void ASimulationController::BeginPlay()
{
	using namespace tinyxml2;
	using std::stoi;
	using std::stof;

	Super::BeginPlay();
    this->simulationOver = false;

	string parametersFileStr(TCHAR_TO_UTF8(*this->parametersFile));
	XMLDocument doc;
	int fileLoadSuccess = doc.LoadFile(parametersFileStr.c_str());
	if (fileLoadSuccess == XML_SUCCESS)
	{
		XMLElement* parent = doc.RootElement();

		this->scenarioCopies = stoi(parent->FirstChildElement("copies")->GetText());
		this->maxLoopDuration = stof(parent->FirstChildElement("duration")->GetText());
		this->tolerances.translationTolerance = stof(parent->FirstChildElement("translation_tolerance")->GetText());
		this->tolerances.rotationTolerance = stof(parent->FirstChildElement("rotation_tolerance")->GetText());
		this->tolerances.translationEpsilon = stof(parent->FirstChildElement("translation_epsilon")->GetText());
		this->logFile = parent->FirstChildElement("log_file")->GetText();

		this->displayConfig.displayRows = stoi(parent->FirstChildElement("display_rows")->GetText());
		this->displayConfig.rowOffset = stof(parent->FirstChildElement("row_offset")->GetText());
		this->displayConfig.columnOffset = stof(parent->FirstChildElement("column_offset")->GetText());
		this->displayConfig.floorOffset = stof(parent->FirstChildElement("floor_offset")->GetText());
		this->displayConfig.copiesPerFloor = stof(parent->FirstChildElement("copies_per_floor")->GetText());

		string descriptionFile = parent->FirstChildElement("description_file")->GetText();
		this->scenarioConfig = ScenarioConfigParser::Load(descriptionFile);
		this->scenarioConfig.simulationType = parent->FirstChildElement("simulation_type")->GetText();

		//optimisation parameters
		this->scenarioConfig.optimisationParams.optimisationDataFile = parent->FirstChildElement("optimisation_data_file")->GetText();
		this->scenarioConfig.optimisationParams.optimisedDataFile = parent->FirstChildElement("optimised_data_file")->GetText();
		this->scenarioConfig.optimisationParams.optimisationScript = parent->FirstChildElement("optimisation_script")->GetText();
		this->scenarioConfig.optimisationParams.keysFile = parent->FirstChildElement("key_file")->GetText();
		this->scenarioConfig.optimisationParams.keys = parent->FirstChildElement("optimisation_keys")->GetText();

		//success rate parameters
		if (parent->FirstChildElement("number_of_trials"))
		{
			this->scenarioConfig.trialData.numberOfTrials = stoi(parent->FirstChildElement("number_of_trials")->GetText());
			this->scenarioConfig.trialData.attemptsPerTrial = stoi(parent->FirstChildElement("attempts_per_trial")->GetText());
			this->scenarioConfig.trialData.resultFile = parent->FirstChildElement("trial_result_file")->GetText();
		}
		else
		{
			this->scenarioConfig.trialData.numberOfTrials = 0;
			this->scenarioConfig.trialData.attemptsPerTrial = 0;
		}

		string optimisationKeysTemp = "";
		for (int i = 0; i < this->scenarioConfig.optimisationParams.keys.length(); i++)
		{
			if (this->scenarioConfig.optimisationParams.keys[i] == '\\' && this->scenarioConfig.optimisationParams.keys[i + 1] == 'n')
			{
				optimisationKeysTemp += '\n';
				i++;
			}
			else
			{
				optimisationKeysTemp += this->scenarioConfig.optimisationParams.keys[i];
			}
		}
		this->scenarioConfig.optimisationParams.keys = optimisationKeysTemp;

		this->scenario = ScenarioFactory::LoadScenario(this->scenarioConfig, this->displayConfig, this->scenarioCopies);
	}
}

void ASimulationController::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (!this->simulationOver)
	{
		if (this->duration > this->maxLoopDuration)
		{
			this->duration = 0.0f;
			if (this->scenarioConfig.simulationType == SimulationTypes::RANDOM || this->scenarioConfig.simulationType == SimulationTypes::ROTATION_OPTIMISED)
			{
				this->scenario->SaveLearningData(this->logFile, this->tolerances);
			}
			else if (this->scenarioConfig.trialData.numberOfTrials > 0)
			{
				this->scenario->UpdateTrials(this->scenarioConfig.trialData, this->tolerances);
				if (this->scenario->TrialsCompleted(this->scenarioConfig.trialData))
				{
					this->scenario->SaveTrialData(this->scenarioConfig.trialData);
					this->simulationOver = true;
					GEngine->AddOnScreenDebugMessage(-1, 2, FColor(255, 0, 0), FString("Simulation over"));
				}
			}

			if (!this->simulationOver)
			{
				this->scenario->UpdateScenario(this->scenarioConfig, this->displayConfig);
			}
		}
		else
		{
			this->duration += DeltaTime;
		}
	}
}
