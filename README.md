# dspbptk
This is dspbptk, the [Dyson Sphere Program](https://store.steampowered.com/app/1366540/Dyson_Sphere_Program/)
Blueprint toolkit. Dyson Sphere Program is an *amazing* factory-building game
by the incredibly talented indie-dev [Youthcat Studio](https://twitter.com/dysonprogram).
It allows blueprinting files to disk and then reusing them in other parts of your game.

There are some cool things that could be done with this import/export
functionality, and what I had in mind was something like:

  * Editing blueprints outside the game, using maybe other/better tools
  * Automatic upgrade/downgrade of blueprints, e.g., upgrading belts Mk1 to Mk2
    or Mk3. This would allow easy generation of a template book (where you
    could e.g., create a set of Mk3 balancers and then automatically create the
    books for Mk1/Mk2 balancers)
  * Automatic parametrization of blueprints, e.g., you have a smelter blueprint
    that requests Titanium ore via an Interstellar Logistics Station, smelts
    them and returns Titanium Ingots. You could update automatically generate the
    same blueprint for iron/copper/silicon/steel so that you don't have to manually
    change the request, assign the Logistics output and change the smelter recipes
    all in one go.
  * Parametric generation of blueprints, e.g., automatically generate a row of
    1, 2, 4, 8, 10 Energy Exchangers/etc.
  * Plot blueprints outside the game, e.g., to generate "birds eye view" of the
    blueprints for library organization.

The possibilities are endless!

Now, all of this can obviously done in the game. So there are two possible solutions that you could take:

  1. Spend some time to do this by hand.
  2. Spends hours reverse engineering DSP and implementing the necessary bits

Obviously, I prefer option (2).


## Why is this difficult?
Dyson Sphere Program kindof "authenticates" blueprints. Essentially, the
blueprint strings are Base64-encoded, gzipped binary data that are also hashed.
This hash function is key: while initially my assumption was that this is MD5,
none of the combinations I tried actually yielded the correct result. So I
reverse engineered the code and found out that actually they do use a
proprietary, modified variant of MD5 that produces completely different
results. They call this algorithm MD5F in their code. There's also a variant
with even other constants, called MD5FC, which I don't know what it is used
for. But it's implemented too.

So essentially, there are two pieces to this puzzle:

  1. Reverse engineer the hash function (done)
  2. Reverse engineer the internal format of the blueprint binary (done)

If anyone from Youthcat Studio reads this: Pleeeease don't make it more
difficult to mod your game. It's fun reversing it and whatnot, but it's also
ultra cool to have a command line tool interface with your game.

## How to use it?
Right now, very little functionality is implemented. But you can kind of see
how it works in the code. For example, there is a command that lets you see
what's in a blueprint:

```
$ ./dspbptk dump "bps/Processor Factory.txt"
Name: Processor Factory
Total building count: 1149
  879  ConveyorBeltMKIII
  183  SorterMKIII
   61  AssemblingMachineMkI
   23  TeslaTower
    2  PlanetaryLogisticsStation
    1  Splitter
```

You can also convert the blueprint to JSON (so you have a very clear idea of
the internal structure of the file). Note that reverse conversion is not
implemented (yet):

```
$ ./dspbptk json --pretty-print "bps/Processor Factory.txt" procfac.json
$ cat procfac.json
[...]
            {
                "area_index": 0,
                "filter_id": 0,
                "index": 16,
                "input_from_slot": 0,
                "input_object_index": 4294967295,
                "input_offset": 0,
                "input_to_slot": 1,
                "item_id": "ConveyorBeltMKIII",
                "local_offset_x": 69.99999237060547,
                "local_offset_x2": 69.99999237060547,
                "local_offset_y": 25.000001907348633,
                "local_offset_y2": 25.000001907348633,
                "local_offset_z": -2.2910537609277526e-06,
                "local_offset_z2": -2.2910537609277526e-06,
                "model_index": 37,
                "output_from_slot": 0,
                "output_object_index": 12,
                "output_offset": 0,
                "output_to_slot": 1,
                "parameter_count": 0,
                "parameters": [],
                "recipe_id": 0,
                "yaw": 315.07470703125,
                "yaw2": 315.07470703125
            },
[...]
```

And there is some example code that edits blueprints, although the only thing
it can do right now is edit the short text. It's mainly to demonstrate that I
can correctly put a blueprint file back together and recompute the correct hash
so that it's accepted in DSP:

```
$ ./dspbptk edit --short-desc "New description" "bps/Processor Factory.txt" new.txt
```


## Thanks
Thanks to Youthcat Studio for an incredible game. You are absolutely fantastic
and your game is ridiculously good and addictive.


## License
GNU GPL-3.
