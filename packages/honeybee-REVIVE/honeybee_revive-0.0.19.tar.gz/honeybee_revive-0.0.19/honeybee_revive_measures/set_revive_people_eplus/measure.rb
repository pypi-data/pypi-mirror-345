class NewMeasure < OpenStudio::Measure::EnergyPlusMeasure
  def name
    # Measure name should be the title case of the class name.
    return 'New Measure'
  end

  def description
    return '.'
  end

  def modeler_description
    return ''
  end

  def arguments(workspace)
    args = OpenStudio::Measure::OSArgumentVector.new
    return args
  end

  def run(workspace, runner, user_arguments)
    super(workspace, runner, user_arguments)  # Do **NOT** remove this line

    # use the built-in error checking
    if !runner.validateUserArguments(arguments(workspace), user_arguments)
      return false
    end

    # -----------------------------------------------------------------------------------
    # Add the new Work Efficiency Schedule
    work_efficiency_schedule = "
    Schedule:Compact,
      rv2024_Resilience_Work_Effic_Schedule,  !- Name
      Fraction,                    !- Schedule Type Limits Name
      Through: 12/31,              !- Field 1
      For: AllDays,                !- Field 2
      Until: 24:00,                !- Field 3
      0.0;                         !- Field 4
    "
    idfObject = OpenStudio::IdfObject.load(work_efficiency_schedule)
    object = idfObject.get
    workspace.addObject(object)

    # -----------------------------------------------------------------------------------
    # Add the new Clothing
    clothing_schedule = "
    Schedule:Compact,
    rv2024_Resilience_Clothing_Schedule,   !- Name
    Any Number,                 !- Schedule Type Limits Name
    Through: 4/30,              !- Field 1
    For: AllDays,               !- Field 2
    Until: 24:00,               !- Field 3
    1.0,                        !- Field 4
    Through: 09/30,             !- Field 5
    For: AllDays,               !- Field 6
    Until: 24:00,               !- Field 7
    0.3,                        !- Field 8
    Through: 12/31,             !- Field 9
    For: AllDays,               !- Field 10
    Until: 24:00,               !- Field 11
    1.0;                        !- Field 12
    "
    idfObject = OpenStudio::IdfObject.load(clothing_schedule)
    object = idfObject.get
    workspace.addObject(object)
    
    # -----------------------------------------------------------------------------------
    # Add the new Air Velocity Schedule
    clothing_schedule = "
    Schedule:Compact,
    rv2024_Resilience_Air_Velocity_Schedule,  !- Name
    Any Number,                   !- Schedule Type Limits Name
    Through: 12/31,               !- Field 1
    For: AllDays,                 !- Field 2
    Until: 24:00,                 !- Field 3
    0.16;                         !- Field 4
    "
    idfObject = OpenStudio::IdfObject.load(clothing_schedule)
    object = idfObject.get
    workspace.addObject(object)

    # -----------------------------------------------------------------------------------
    # Get all People objects in the model
    people_objects = workspace.getObjectsByType('People'.to_IddObjectType)

    # Check if any People objects are found
    if people_objects.empty?
      runner.registerAsNotApplicable('No People objects found in the model.')
      return true
    end

    # Iterate over each people object and add the new attribute
    people_objects.each do |people_object|
      new_people_string = "
      People,
        rv2024_Resilience_People,      !- Name
        #{people_object.getString(1)},      !- Zone or ZoneList or Space or SpaceList Name
        #{people_object.getString(2)},      !- Number of People Schedule Name
        #{people_object.getString(3)},      !- Number of People Calculation Method
        #{people_object.getString(4)},      !- Number of People
        #{people_object.getString(5)},      !- People per Floor Area {person/m2}
        #{people_object.getString(6)},      !- Floor Area per Person {m2/person}
        #{people_object.getString(7)},      !- Fraction Radiant
        #{people_object.getString(8)},      !- Sensible Heat Fraction
        #{people_object.getString(9)},      !- Activity Level Schedule Name
        0.0000000382,                       !- Carbon Dioxide Generation Rate {m3/s-W}
        No,                                 !- Enable ASHRAE 55 Comfort Warnings
        ,                                   !- Mean Radiant Temperature Calculation Type
        ,                                   !- Surface Name/Angle Factor List Name
        rv2024_Resilience_Work_Effic_Schedule,         !- Work Efficiency Schedule Name
        ClothingInsulationSchedule,         !- Clothing Insulation Calculation Method
        rv2024_Resilience_Clothing_Schedule,           !- Clothing Insulation Calculation Method Schedule Name
        rv2024_Resilience_Clothing_Schedule,           !- Clothing Insulation Schedule Name
        rv2024_Resilience_Air_Velocity_Schedule,       !- Air Velocity Schedule Name
        Pierce;                             !- Thermal Comfort Model 1 Type
      "
      idfObject = OpenStudio::IdfObject.load(new_people_string)
      object = idfObject.get
      workspace.addObject(object)

      # Remove the original People object from the Model
      workspace.removeObject(people_object.handle)
    end

    return true
  end
end

# register the measure to be used by the application
NewMeasure.new.registerWithApplication
