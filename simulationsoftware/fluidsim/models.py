from django.db import models
# Create your models here.

class Modules(models.Model):
    name = models.CharField(max_length=100,unique=True)

class SubModules(models.Model):
    module = models.ForeignKey(Modules, on_delete=models.CASCADE, related_name='submodules')
    name = models.CharField(max_length=100,unique=False)


from django.contrib.auth.models import User
class UserModuleAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Modules, on_delete=models.CASCADE)

class UserSubmoduleAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submodule = models.ForeignKey(SubModules, on_delete=models.CASCADE)

class LogicBlocks(models.Model):
    module_id = models.ForeignKey(Modules,null=False,on_delete=models.CASCADE)
    submodule_id = models.ForeignKey(SubModules,null=False,on_delete=models.CASCADE,related_name="logic_blocks")
    name = models.CharField(max_length=40,null=False,unique=True,default="NONE")
    block_type = models.CharField(max_length=40)
    mode = models.CharField(max_length=40)
    publish = models.BooleanField(default=False,null=False)

# logic blocks params tables
class LogicBlocksDesignParams(models.Model):
    LB_id = models.ForeignKey(LogicBlocks,null=False,on_delete=models.CASCADE,related_name="logic_block_design")
    param_name = models.CharField(max_length=130,null=False,default='NONE')
    unit = models.CharField(max_length=130,null=False,default='NONE')

class LogicBlocksPerformanceParams(models.Model):
    LB_id = models.ForeignKey(LogicBlocks,null=False,on_delete=models.CASCADE)
    param_name = models.CharField(max_length=130,null=False,default='NONE')
    unit = models.CharField(max_length=130,null=False,default='NONE')

class LogicBlocksLifingParams(models.Model):
    LB_id = models.ForeignKey(LogicBlocks,null=False,on_delete=models.CASCADE)
    param_name = models.CharField(max_length=130,null=False,default='NONE')
    unit = models.CharField(max_length=130,null=False,default='NONE') 

class LogicBlocksPrognosticParams(models.Model):
    LB_id = models.ForeignKey(LogicBlocks,null=False,on_delete=models.CASCADE)
    param_name = models.CharField(max_length=130,null=False,default='NONE')
    unit = models.CharField(max_length=130,null=False,default='NONE')

class LogicBlockDesignOutputs(models.Model):
    LB_id = models.ForeignKey(LogicBlocks,null=False,on_delete=models.CASCADE)
    out_param_name = models.CharField(max_length=130,null=False,default='NONE')
    unit = models.CharField(max_length=130,null=False,default='NONE')

class LogicBlockLifingOutputs(models.Model):
    LB_id = models.ForeignKey(LogicBlocks,null=False,on_delete=models.CASCADE)
    out_param_name = models.CharField(max_length=130,null=False,default='NONE')
    unit = models.CharField(max_length=130,null=False,default='NONE')

class LogicBlockPerformanceOutputs(models.Model):
    LB_id = models.ForeignKey(LogicBlocks,null=False,on_delete=models.CASCADE)
    out_param_name = models.CharField(max_length=130,null=False,default='NONE')
    unit = models.CharField(max_length=130,null=False,default='NONE')

class LogicBlockPrognosticOutputs(models.Model):
    LB_id = models.ForeignKey(LogicBlocks,null=False,on_delete=models.CASCADE)
    out_param_name = models.CharField(max_length=130,null=False,default='NONE')
    unit = models.CharField(max_length=130,null=False,default='NONE')

# network, function block and connection realted tables
class Network(models.Model):
    name = models.TextField(null=False,default="NO NAME")
    network_type = models.TextField(null=False,default="NONE")

class functionBlockData(models.Model):
    id = models.TextField(primary_key=True)
    proxy_name = models.CharField(max_length=50,null=True,unique=True)
    true_LB_id = models.ForeignKey(LogicBlocks,on_delete=models.CASCADE,null=True)
    network_id = models.ForeignKey(Network,on_delete=models.CASCADE,null=True)

class Connections(models.Model):
    source = models.ForeignKey(functionBlockData,on_delete=models.CASCADE, related_name="source_connections")
    destination = models.ForeignKey(functionBlockData,on_delete=models.CASCADE, related_name="destination_connections",null=True,blank=True)
    network_id = models.ForeignKey(Network,on_delete=models.CASCADE,null=True)

