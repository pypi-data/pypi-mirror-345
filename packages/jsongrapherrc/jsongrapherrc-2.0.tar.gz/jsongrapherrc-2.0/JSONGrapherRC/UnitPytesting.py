import unitpy

print(unitpy.U("kg/m"))


print(unitpy.U("(((kg)/m))/s"))

units1 = unitpy.U("(((kg)/m))/s")
units2 = unitpy.U("(((g)/m))/s")
unitsRatio = units1/units2
print(unitsRatio)

print(units2)
units1multiplied =1*unitpy.U("(((kg)/m))/s")
print("line 14")
ratioWithUnits = units1multiplied.to("(((g)/m))/s")
print(ratioWithUnits)
print(str(ratioWithUnits).split(' '))

units1 = unitpy.Q("1 (((kg)/m))/s")
units2 = unitpy.Q("1 (((g)/m))/s")
unitsRatio = units1/units2
print(unitsRatio)
