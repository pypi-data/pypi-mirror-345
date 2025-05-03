# Blueprint Domain Populator

Create a separate [TclRAL](https://repos.modelrealization.com/cgi-bin/fossil/tclral/index) domain database for each
Domain in your System.

Let's say you have modeled an Elevator System with Elevator Management, Transport, and Signal IO domains.

You use the Blueprint Domain Populator to create three TclRAL databases, each populated with whatever initial instance populations
you have defined in a supplied context.

## Installation

% pip install mi-domain-populate

This creates an executable command named `domaindb`

Type domaindb -help to get the complete and most up to date list of supported options.

## Usage

This package takes three inputs, a system populated into the metamodel database, a context specifying initial
instance populates, and a map from domain to system data types.

## Command usage

`% domaindb -s mmdb_elevator.ral -c EVMAN_one_bank1.sip -t EVMAN_types.yaml -o`

Here -s is the system, -c is the context, and -t specifies the mapping of domain types to available system
data types which currently are TclRAL types. If you use the optional -o option, a separate `<domain alias>.txt` file will be
generated for each domain database. For the above command you should see these files generated:

`elevator.ral` and `evman.txt`

To get the above example copied into your current working directory use the -E (example) option.

`% domaindb -E`

### System

This is a metamodel TclRAL database (*.ral) file populated with a user's domain model: the Elevator Management domain populated into the Shlaer-Mellor metamodel, for example. It is probably named `elevator_mmdb.ral`

This *.ral file is produced by the modeldb command if you have the xuml-populate package installed.

### Context

A scenario instance population *.sip file that you write yourself which specifies instances and current states to be populated into your domain database. This file defines a context that can be used in a variety of simulation scenarios in a downstream package currently under development called model execute.

### Type Mapping

A yaml file that maps each domain type to a TclRAL system type.


