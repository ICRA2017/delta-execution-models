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

#include "Scenario.h"

class ContainerScenario : public Scenario
{
public:
	ContainerScenario(ScenarioConfig& scenarioConfig, const DisplayConfig& displayConfig, int copies);
	virtual void SaveLearningData(const string& file, const Tolerances& tolerances) const;
    virtual void UpdateTrials(TrialData& trialData, const Tolerances& tolerances);
protected:
	virtual bool IsSuccessful(const Objects& objects, int idx, const Tolerances& tolerances) const;
};
