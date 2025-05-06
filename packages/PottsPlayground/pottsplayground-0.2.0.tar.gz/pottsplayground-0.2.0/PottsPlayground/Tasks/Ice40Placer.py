import numpy
import networkx as nx
from matplotlib import pyplot as plt
import PottsPlayground #import includes self. What will happen? No obvious issues.  Maybe the interpreter knows not to make this a circular thing.
from PottsPlayground.Tasks import BaseTask
from PottsPlayground.Tasks.GraphColoring import GraphColoring
import math
import time
import pickle
import copy
from collections import defaultdict

def GetCellPortNetName(cell, name):
	if cell.ports[name].net is not None:
		return cell.ports[name].net.name
	else:
		return None

def RecurseDownCarryChain(ctx, cell):
		#recursively finds the next cell in a carry chain, returning a list of all cells downwind of the given cell
		nn = GetCellPortNetName(cell, 'COUT')
		if nn is None:
			return [cell] #last cell in the carry chain
		net = ctx.nets[nn]
		return [cell] + RecurseDownCarryChain(ctx, net.users[0].cell)

def DffIncompatible(cell1, cell2):
	if (cell1.params['DFF_ENABLE']=='1') and (cell2.params['DFF_ENABLE']=='1'):
		if ((GetCellPortNetName(cell1, 'CEN') != GetCellPortNetName(cell2, 'CEN')) or
			(GetCellPortNetName(cell1, 'CLK') != GetCellPortNetName(cell2, 'CLK')) or
			(GetCellPortNetName(cell1, 'SR')  != GetCellPortNetName(cell2, 'SR'))  or
			(cell1.params['NEG_CLK'] != cell2.params['NEG_CLK'])):
				return True
	return False

def timing_paths(ctx):
	LC_in_ports = ["I0", "I1", "I2", "I3", "CIN"]

	#first, create directed graph where each node is a net,
	#and edges are non-dff cells between nets.
	G = nx.DiGraph()
	for key, net in ctx.nets:
		G.add_node(net.name, depth=1)

	for key, cell in ctx.cells:
		if cell.type != "ICESTORM_LC":
			continue #timing only for logic cells

		input_net_names = [(port, GetCellPortNetName(cell, port)) for port in LC_in_ports]
		input_net_names = [info for info in input_net_names if info[1] != None]

		output_net_names = []
		if cell.params['DFF_ENABLE'] == "0" and GetCellPortNetName(cell, 'O') is not None:
			output_net_names.append(('O', GetCellPortNetName(cell, 'O')))
		if GetCellPortNetName(cell, 'COUT') is not None:
			output_net_names.append(('COUT', GetCellPortNetName(cell, 'COUT')))

		for inp in input_net_names:
			for out in output_net_names:
				w = 0.1 if (inp[0] == 'CIN' and out == 'COUT') else 1.
				#carry connections are automatically very fast,
				#so should not be fully counted towards timing arc length
				G.add_edge(inp[1], out[1], weight=w)

	#delete two special nets that nextpnr uses:
	for special_node in ["$PACKER_VCC_NET", "$PACKER_GND_NET"]:
		if special_node in G:
			G.remove_node(special_node)

	# print(sorted(nx.simple_cycles(G)))
	assert len(sorted(nx.simple_cycles(G))) == 0

	#to figure out how important each net is to timing, traverse the graph
	#forwards and backwards, adding up the lengths each way.
	#after adding up, nodes in G_forward will know how the maximum depth
	#of nets before them, and G_reverse will know the maximum depth after.
	#adding the two gives the length of the longest pathway that passes through each net.
	#To make sure that each net really knows its maximum before or after length,
	#graph edges are deleted as they are followed and edges are only followed once all the 
	#preceding edges have been processed and deleted.
	G_forward = copy.deepcopy(G)
	G_reverse = copy.deepcopy(G)

	while (G_forward.number_of_edges() > 0):
		# print(G_forward.number_of_edges())
		for net in G_forward.nodes:
			if len(G_forward.in_edges(net)) == 0:
				to_remove = []
				for u, v, edge_data in G_forward.out_edges(net, data=True):
					G_forward.nodes[v]['depth'] = max(G_forward.nodes[v]['depth'], G_forward.nodes[u]['depth']+edge_data['weight'])
					# print(G.nodes[v]['depth'], G.nodes[u]['depth'], edge_data['weight'])
					to_remove.append((u, v))
				G_forward.remove_edges_from(to_remove)

	while (G_reverse.number_of_edges() > 0):
		# print(G_reverse.number_of_edges(), G_reverse.number_of_nodes())
		for net in G_reverse.nodes:
			if len(G_reverse.out_edges(net)) == 0:
				to_remove = []
				for u, v, edge_data in G_reverse.in_edges(net, data=True):
					G_reverse.nodes[u]['depth'] = max(G_reverse.nodes[u]['depth'], G_reverse.nodes[v]['depth']+edge_data['weight'])
					to_remove.append((u, v))
				G_reverse.remove_edges_from(to_remove)

	#combine forward and reverse counts:
	arc_lengths = defaultdict(lambda:1)
	for net in G.nodes:
		# print(G_reverse[net], G_forward[net])
		combined = G_reverse.nodes[net]['depth'] + G_forward.nodes[net]['depth'] - 1
		arc_lengths[net] = combined

	return arc_lengths

def label_carry_chains(ctx):
	for key, cell in ctx.cells:
		if cell.type == "ICESTORM_LC" and GetCellPortNetName(cell, 'COUT') is not None and GetCellPortNetName(cell, 'CIN') is None:
			#then this is the start of a chain!
			chain = RecurseDownCarryChain(ctx, cell)
			[chain_cell.setAttr("type", "CCchild") for chain_cell in chain] #re-type cells to indicate they are in a carry chain
			# [chain_cell.setAttr("CC", cell.name) for chain_cell in chain] 
			cell.setAttr("type", "CC") #re-type root cells

def label_lc_subtypes(ctx):
	for i, (key, cell) in enumerate(ctx.cells):
		if cell.type == "ICESTORM_LC":
			continue
		if "BEL" in cell.attrs:
			bel = cell.attrs["BEL"]
			loc = ctx.getBelLocation(bel)
			cell.setAttr("SubType", "%i"%loc.z)
		else:
			cell.setAttr("SubType", "%i"%i)

def gather_bel_types(ctx):
	BelTypes = defaultdict(list)
	# self.GetBelType = {} #replicate ctx functionality, so that I can easily, temporarily keep track of artificial bel type changes
	for bel in ctx.getBels():
		bel_type = ctx.getBelType(bel)
		# self.GetBelType[bel] = bel_type
		BelTypes[bel_type].append(bel)

	for i, bel in enumerate(BelTypes['ICESTORM_LC']):
		loc = ctx.getBelLocation(bel)
		BelTypes["LC%i"%(loc.z)].append(bel)
		# self.GetBelType[bel] = "LC%i"%loc.z

	BelTypes['CC'] = BelTypes['LC0'] #artificial mapping, so code below can apply more uniformly

	return BelTypes


class Ice40Placer(BaseTask.BaseTask):
	"""
	Potts Model that corresponds to placing logic elements in an Ice40 FPGA.  Ties in with the NextPNR tool;
	is not 100% functional, but can be used to place many FPGA designs.  Supports LUTs, carry chains, and IO.
	"""

	def __init__(self, ctx, cost_balancing=(15, 0.5, 1, 0), split_cells=True, verbose=False):
		"""
		Creates a model of FPGA placement given a NextPNR context.  The context is available when running a Python script inside of
		the NextPNR tool.  The context includes both information about the specific FPGA (availability and locations of physical Basic ELements i.e. BELs)
		and about the design that needs to be placed (logical BELs and their connectivity).  There are several different optimization objectives that
		can be balanced.  The first objective, 'exclusion', is mandatory, since it enforces that multiple logical BELs are not assigned to
		the same physical BEL.  'wirelen' tries to minimize overall distance between connected logical BELs; 'timing' weighs critical path connections
		more to keep the critical path as fast as possible; and 'jogs' tries to assign connected BELs to the same row or column so that 
		only a single horizontal or vertical routing channel is needed to connect them.

		:param ctx: A NextPNR context opbject.
		:param cost_balancing: Specifies relative weight of different optimization objectives. Objectives are (exclusion, wirelen, timing, jogs)
		:type cost_balancing: tuple
		:param split_cells: FPGA LUTs are grouped in blocks of eight; each of the eight have nearly similar connectivity.  If split_cells is True,
		each logical LUT is pre-constrained to one of the eight LUT positions.  This reduces the optimization space for faster results.
		:type split_cells: boolean
		:type verbose: boolean
		"""

		#======================================================construct friendlier formats of the design specifications
		#get lists of bel types in the architecture:
		BaseTask.BaseTask.__init__(self)
		exclusion_factor = cost_balancing[0]
		w_wirelen = cost_balancing[1]
		w_timing = cost_balancing[2]
		w_jogs = cost_balancing[3]

		net_timing_info = timing_paths(ctx)
		arc_lengths = [value for key, value in net_timing_info.items()]
		print("arc lengths", numpy.unique(arc_lengths, return_counts=True))
		longest_arc = numpy.max(arc_lengths)
		# print("Longest arc", longest_arc)

		label_carry_chains(ctx)
		
		if split_cells:
			label_lc_subtypes(ctx)

		self.BelTypes = gather_bel_types(ctx)
			

		#subdivide global buffer bels based on even-oddness, since they have slightly different features
		wire_names = [ctx.getBelPinWire(bel, "GLOBAL_BUFFER_OUTPUT") for bel in self.BelTypes["SB_GB"]]
		net_nums = [int(wire_name[-1]) for wire_name in wire_names]
		even_global_buffers = [i for i, netnum in enumerate(net_nums) if netnum%2 == 0]
		odd_global_buffers =  [i for i, netnum in enumerate(net_nums) if netnum%2 == 1]

		#get a sub-list of logic blocks that are not at the top,
		#i.e. ones that are not limited to length-8 carry chains
		bel_loc = [ctx.getBelLocation(bel) for bel in self.BelTypes['CC']]
		bel_y = [loc.y for loc in bel_loc]
		ymax = numpy.max(bel_y)
		constrain2lowerY = [i for i, y in enumerate(bel_y) if y != ymax]
		
		#======================================================= partition construction
		self.used_bels = []
		for key, cell in ctx.cells:
			if cell.type == "CCchild":
				continue #these are not explicitly included in the optimization

			self.AddSpins([len(self.BelTypes[cell.type])], [cell.name])

			# not all global buffers can drive all signal types.
			# Must restrict certain global buffer cells to a subset of physical global buffers:
			if cell.type == "SB_GB":
				users = cell.ports["GLOBAL_BUFFER_OUTPUT"].net.users
				user_ports = [user.port for user in users]
				if "CEN" in user_ports:
					self.PinSpin(cell.name, odd_global_buffers)

			if cell.type == "CC":
				self.PinSpin(cell.name, constrain2lowerY)

			#if a cell has already been fixed for some reason (like IO),
			#fix it in the Potts model here too:
			if "BEL" in cell.attrs:
				bel = cell.attrs["BEL"]
				self.used_bels.append(bel)
				bel_position = self.BelTypes[cell.type].index(bel)
				self.PinSpin(cell.name, [bel_position])


		
			# print("")
			# for thing in dir(cell):
				# print(thing)
			# for k, v in cell.ports:
				# print(k, v)
				# for thing in v.net.users:
					# print(thing.port)
					# for thing2 in dir(thing.port):
						# print(thing2)
			# for k, v in cell.attrs:
				# print(k, v)

		# exit()

		
		# ============================================================================= kernel map construction
		


		#I'm not quite sure what I was doing here.  It's not critical to functioning, so let's ignore it for now
		# total_weight_strength = numpy.zeros([nPartitions])
		# for i, cell1_name in enumerate(self.Partitions2CellNames):
		# 	for j, cell2_name in enumerate(self.Partitions2CellNames):
		# 		if G.has_edge(cell1_name, cell2_name):
		# 			data = G[cell1_name][cell2_name]
		# 			nEndpoints = data["w"]
		# 			total_weight_strength[i] = total_weight_strength[i] + w_wirelen/nEndpoints
		# 			d2u = data["d2u"]
		# 			if "ArcsAfter" in data and "ArcsBefore" in data:
		# 				narcs = data["ArcsAfter"]+data["ArcsBefore"]+1
		# 				total_weight_strength[i] = total_weight_strength[i] + w_timing*2**(narcs-maxnarc)
		# 				total_weight_strength[i] = total_weight_strength[i] + w_jogs

		# print(total_weight_strength)

		lc_check_types = ["LC%i"%i for i in range(8)] + ["CC", "ICESTORM_LC"]

		#set up ntiles variables, which tells if a cell occupies 1 or more than 1 logic tiles (if it is a carry chain)
		ntiles = {}
		for key, cell in ctx.cells:
			if cell.type == "CC":
				ntiles[cell.name] = math.ceil(len(RecurseDownCarryChain(ctx, cell))/8)
			else:
				ntiles[cell.name] = 1

		for key1, cell1 in ctx.cells:
			if cell1.type == "CCchild":
				continue #these are not explicitly included in the optimization
			for key2, cell2 in ctx.cells:
				if cell2.type == "CCchild":
					continue #these are not explicitly included in the optimization
				if cell1.name == cell2.name:
					continue

				#there are two types of hard constraints, bel exclusion and tile exclusion.
				#Bel exclusion means that two cells have the same type, and therefore cannot
				#be in the same place.  Simple.
				#Tile exclusion means that two cells cannot even be in the same tile,
				#due to various factors.  A carry chain in one tile might even exclude
				#other cells in the tile above it, if the chain is longer than 8.

				
				tile_exclude = False
				
				#two logic cells with different D flip flop configurations cannot share the same logic tile
				if cell1.type in lc_check_types and cell2.type in lc_check_types:
					tile_exclude = DffIncompatible(cell1, cell2)

				#if a cell is a carry chain, it may span across more than one tile,
				#in which case we should have a multi-tile exclusion.
				#we must also account for when two multi-length carry chains exclude each other.
				ntiles1 = ntiles[cell1.name]
				ntiles2 = ntiles[cell2.name]

				#create a structural penalty to prevent cells from sharing the same FPGA resources
				#(applies to the mutual exclusion of carry chains and logic cells too)
				if (cell1.type == "CC" and cell2.type in lc_check_types):
					tile_exclude = True
				if (cell2.type == "CC" and cell1.type in lc_check_types):
					tile_exclude = True

				wgt = 1*exclusion_factor
				if tile_exclude:
					self.AddKernel(lambda n: self.TileExclusion(ctx, cell1.type, cell2.type, ntiles1, ntiles2, n), cell1.name, cell2.name, weight=wgt)

				elif cell1.type == cell2.type:
					self.AddKernel(lambda n: self.BelExclusion(n), cell1.name, cell2.name, weight=wgt)


		#new loop through nets, to add net constraints.
		#actually, could do this later.  It's a secondary goal...
				#determine the wiring connectivity between the two cells,
				# connected = False
				# if G.has_edge(cell1_name, cell2_name):
				# 	connected = True #the heavy lifting and case handling has been done elsewhere, in the construction of G
				# 	data = G[cell1_name][cell2_name]
				# 	nEndpoints = data["w"]
				# 	d2u = data["d2u"]
				# 	if "ArcsAfter" in data and "ArcsBefore" in data:
				# 		narcs = data["ArcsAfter"]+data["ArcsBefore"]+1

				# #a geometric mean of how constrained each cell is determines how much constraint weight there should be
				# wgt = 1+total_weight_strength[i]*total_weight_strength[j]/(total_weight_strength[i] + total_weight_strength[j])

				# # =====================================================main if-else to decide which kernel, if any, relates each pair of cells
				# if i==j:
				# 	#the assigned position of one cell should not feed back upon itself
				# 	continue

				# if connected and d2u:
				# 	self.AddKernel(lambda n: self.NoJogsKernel(ctx, type1, type2, n), i, j, weight=w_jogs)
				# 	self.AddKernel(lambda n: self.TimingKernel(ctx, type1, type2, n), i, j, weight=w_timing*2**(narcs-maxnarc))

				# elif connected:
				# 	self.AddKernel(lambda n: self.WirelenKernel(ctx, type1, type2, n), i, j, weight=w_wirelen/nEndpoints)


		self.CompileKernels() #a baseTask function


		#revert altered types:
		for key, cell in ctx.cells:
			if cell.type.startswith("CC") or cell.type.startswith("LC"):
				cell.setAttr("type", "ICESTORM_LC")
			# print(cell.type)

	

	def SetResultInContext(self, ctx, state):
		"""
		Takes the final state of an annealing run and configures that result into the nextpnr context.
		The context is not returned but afterwards should contain added constraints corresponding to the given state.

		:param ctx: NextPNR context corresponding to the PlacerTask.
		:param state: A Potts model state.
		:type state: 1-D Numpy int array
		:return: Number of conflicts, i.e. number of BELs assigned to incompatible physical locations.  Should be 0 for a successful run.
		:rtype: int
		"""
		nConflicts = 0
		for i, q in enumerate(state):
			# if i > 5:
				# return
			cell_name = self.Partitions2CellNames[i]
			cell = ctx.cells[cell_name]
			if "BEL" in cell.attrs:
				#this cell was previously constrained, so we don't set it:
				continue
			cell_type = self.GetCellType[cell_name]
			if cell_type == "CC":
				chain = [ctx.cells[cn] for cn in self.chains[cell_name]]
				root_bel = self.BelTypes['LC0'][q]
				print("constraining length", len(chain), "carry chain with cell", cell_name,  "rooted at bel", root_bel)
				for j, cell in enumerate(chain):
					LCtype = "LC%i"%(j%8)
					bel = self.BelTypes[LCtype][q+int(j/8)]#move to the next tile for each 8 logic cells
					if bel not in self.used_bels:
						cell.setAttr("BEL", bel)
						# ctx.bindBel(bel, cell, STRENGTH_STRONG)
						self.used_bels.append(bel)
					else:
						print("Error, cell %s cannot be assigned to bel %s which is already assigned"%(cell_name, bel))
						nConflicts = nConflicts + 1
			else: #all other things that are not carry chains
				bel = self.BelTypes[cell_type][q]
				# print(cell.name, bel)
				# if (ctx.checkBelAvail(bel)):
				if bel not in self.used_bels:
					# ctx.bindBel(bel, cell, strength)
					cell.setAttr("BEL", bel)
					# ctx.bindBel(bel, cell, STRENGTH_STRONG)
					self.used_bels.append(bel)
					# cell.attrs["BEL"] = bel
				else:
					print("Error, cell %s cannot be assigned to bel %s which is already assigned"%(cell_name, bel))
					nConflicts = nConflicts + 1

		return nConflicts

	# =============================================================================================== kernel generators
	# =================================================================================================================
	def get_type_locs(self, ctx, type1):
		locs1 = numpy.zeros([len(self.BelTypes[type1]), 2])
		for i, bel1 in enumerate(self.BelTypes[type1]):
			loc1 = ctx.getBelLocation(bel1)
			locs1[i, 0] = loc1.x
			locs1[i, 1] = loc1.y
		return locs1

	def NoJogsKernel(self, ctx, type1, type2, n=False):
		if type1.startswith("LC") or type1 == "CC":
			type1 = "LC0"
		if type2.startswith("LC") or type2 == "CC":
			type2 = "LC0" #has to be set to a specific type, so that it can find the right bel distances

		name = "NoJogs between types " + type1 + " and " + type2

		if n:
			return name
		elif name in self.KernelDict:
			#prevent redundant construction (possibly caused by constructing compound kernels)
			return self.KernelList[self.KernelDict[name]]

		locs1 = self.get_type_locs(ctx, type1)
		locs2 = self.get_type_locs(ctx, type2)
		locs1 = numpy.expand_dims(locs1, 1)
		locs2 = numpy.expand_dims(locs2, 0)

		dx = numpy.abs(locs1[:,:,0]-locs2[:,:,0])
		dy = numpy.abs(locs1[:,:,1]-locs2[:,:,1])

		local_conn = (dx <= 1)*(dy<=1)*1
		dx_conn = (dx > 1)*(dy == 0) * 1
		dy_conn = (dy > 1)*(dx == 0) * 1
		distant_conn = (local_conn == 0)*(dx_conn == 0)*(dy_conn == 0)*(10+(dx+dy))

		return distant_conn

	def TimingKernel(self, ctx, type1, type2, n=False):
		#LC and carry chain types all use the same resource type, and have the same kernel size, so they share the same wirelen kernels
		if type1.startswith("LC") or type1 == "CC":
			type1 = "LC0"
		if type2.startswith("LC") or type2 == "CC":
			type2 = "LC0" #has to be set to a specific type, so that it can find the right bel distances

		name = "Timing between types " + type1 + " and " + type2

		if n:
			return name
		elif name in self.KernelDict:
			#prevent redundant construction (possibly caused by constructing compound kernels)
			return self.KernelList[self.KernelDict[name]]

		locs1 = self.get_type_locs(ctx, type1)
		locs2 = self.get_type_locs(ctx, type2)
		locs1 = numpy.expand_dims(locs1, 1)
		locs2 = numpy.expand_dims(locs2, 0)

		dx = numpy.abs(locs1[:,:,0]-locs2[:,:,0])
		dy = numpy.abs(locs1[:,:,1]-locs2[:,:,1])

		local_conn = (dx <= 1)*(dy<=1)*0.6
		dx_conn = (dx > 1)*(dy == 0) * (dx + 5)
		dy_conn = (dy > 1)*(dx == 0) * (dy + 5)
		distant_conn = (local_conn == 0)*(dx_conn == 0)*(dy_conn == 0)*3*(3+dx+dy)

		return dx_conn + dy_conn + distant_conn

	def WirelenKernel(self, ctx, type1, type2, n=False):
		#LC and carry chain type all use the same resource type, and have the same kernel size, so they share the same wirelen kernels
		if type1.startswith("LC") or type1 == "CC":
			type1 = "LC0"
		if type2.startswith("LC") or type2 == "CC":
			type2 = "LC0" #has to be set to a specific type, so that it can find the right bel distances

		name = "Wirelength between types " + type1 + " and " + type2

		if n:
			return name
		elif name in self.KernelDict:
			#prevent redundant construction (possibly caused by constructing compound kernels)
			return self.KernelList[self.KernelDict[name]]

		locs1 = self.get_type_locs(ctx, type1)
		locs2 = self.get_type_locs(ctx, type2)
		locs1 = numpy.expand_dims(locs1, 1)
		locs2 = numpy.expand_dims(locs2, 0)

		dx = numpy.abs(locs1[:,:,0]-locs2[:,:,0])
		dy = numpy.abs(locs1[:,:,1]-locs2[:,:,1])

		return dx + dy

	def TileExclusion(self, ctx, type1, type2, ntiles2, ntiles1, n=False):
		#LC and carry chain types all use the same resource type, and have the same kernel size, so they share the same wirelen kernels
		if type1.startswith("LC") or type1 == "CC":
			type1 = "LC0"
		if type2.startswith("LC") or type2 == "CC":
			type2 = "LC0" #has to be set to a specific type, so that it can find the right bel distances

		if n:
			return "TileExclusion-%s-%s-%i-%i"%(type1, type2, ntiles1, ntiles2)

		#numpy-vectorized kernel construction for improved speed
		locs1 = self.get_type_locs(ctx, type1)
		locs2 = self.get_type_locs(ctx, type2)
		locs1 = numpy.expand_dims(locs1, 1)
		locs2 = numpy.expand_dims(locs2, 0)

		loc1y = locs1[:,:,1]
		loc1x = locs1[:,:,0]
		loc2y = locs2[:,:,1]
		loc2x = locs2[:,:,0]
		return (loc1y-ntiles1 < loc2y)*(loc2y < loc1y+ntiles2)*(loc1x == loc2x)

	def BelExclusion(self, n=False):
		if n:
			return "BelExclusion"

		qMax = numpy.max([len(bels) for bels in self.BelTypes])
		return numpy.eye(qMax)


	def examine_path(self, path_cell_names):

		for i in range(1, len(path_cell_names)):
			cell1 = path_cell_names[i-1]
			cell2 = path_cell_names[i]
			if cell1 in self.G and cell2 in self.G:
				print(self.G[cell1][cell2])


if __name__ == '__main__':
	#alternate version that makes direct edits to the ctx instead of creating a parallel accounting structure:
	for key, cell in ctx.cells:
		if GetCellPortNetName(cell, 'COUT') is not None and GetCellPortNetName(cell, 'CIN') is None:
			#then this is the start of a chain!
			chain = RecurseDownCarryChain(ctx, cell)
			[chain_cell.setAttr("type", "CC") for chain_cell in chain] #re-type cells to indicate they are in a carry chain
			ctx.setAttr("type", "CCroot") #re-type root cells

	exit()

	placer = Ice40Placer(ctx, cost_balancing=(15, 0.5, 1, 0.1))
	tstart = time.perf_counter()
	results = Annealing.Anneal(vars(placer), placer.defaultTemp(niters=5e6, tmax=12), OptsPerThrd=1, TakeAllOptions=True, backend="PottsJit", substrate="CPU", nReplicates=1, nWorkers=1, nReports=1)
	ttot = time.perf_counter() - tstart
	print("Annealing time is %.2f seconds"%ttot) 

	placer.SetResultInContext(ctx, results['MinStates'][-1,:])