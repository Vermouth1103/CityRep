import networkx as nx
import math
from logging import getLogger
from libcity.model.abstract_traffic_tradition_model import AbstractTraditionModel
from libcity.utils.GPS_utils import radian2angle, R_EARTH, angle2radian, dist, init_bearing
import numpy as np


class IVMM(AbstractTraditionModel):
    """
    IVMM
    """

    def __init__(self, config, data_feature):

        super().__init__(config, data_feature)

        # logger
        self._logger = getLogger()

        # model param
        self.k = config.get('k', 5)  # maximum number of candidates of any sampling points
        self.r = config.get('r', 100)  # radius of road segment candidate
        self.mu = config.get('mu', 0)
        self.sigma = config.get('sigma', 10)
        self.beta = config.get('beta', 40)
        self.window_size = config.get('window_size', 40)

        # data param
        self.with_time = data_feature.get('with_time', True)
        self.with_rd_speed = data_feature.get('with_rd_speed', True)
        self.delta_time = data_feature.get('delta_time', True)

        # data cache
        self.rd_nwk = None
        self.tra_id = None
        self.trajectory = None
        self.candidates = list()
        self.res_dct = dict()

        # To facilitate the search of candidate points, the road network is indexed using a grid.
        self.lon_r = None
        self.lat_r = None

    def run(self, data):
        # road network & trajectory
        self.rd_nwk = data['rd_nwk']
        trajectory = data['trajectory']

        # set lon_radius and lat_radius based on the first Node of rd_nwk
        self._set_lon_lat_radius(
            self.rd_nwk.nodes[list(self.rd_nwk.nodes)[0]]['lon'],
            self.rd_nwk.nodes[list(self.rd_nwk.nodes)[0]]['lat']
        )

        # deal with every trajectories
        for usr_id, usr_value in trajectory.items():
            self.usr_id = usr_id
            for traj_id, value in usr_value.items():
                self._logger.info('begin map matching, usr_id:%d traj_id:%d' % (usr_id, traj_id))
                self.traj_id = traj_id
                self.trajectory = value
                self._run_one_tra()
                self._logger.info('finish map matching, usr_id:%d traj_id:%d' % (usr_id, traj_id))
        return self.res_dct

    def _run_one_tra(self):
        """
        run ST-Matching for one trajectory
        self.trajectory self.rd_nwk
        Returns:
        """
        self._get_candidates()
        self._logger.info('finish getting candidates')
        self._observation_probability()
        self._logger.info('finish calculating observation probability')
        self._transmission_probability()
        self._logger.info('finish calculating transmission probability')
        if self.with_rd_speed and self.with_time:
            self._temporal_analysis()
            self._logger.info('finish spatial analysis')
        self._score_matrix()
        self._logger.info('finish building score matrix')
        self._interactive_voting()
        self._logger.info('finish interactive voting')
        self._find_matched_sequence()
        self._logger.info('finish finding matched sequence')

    def _set_lon_lat_radius(self, lon, lat):
        """
        get longitude range & latitude range (because radius is actually achieved by a grid search)
        Args:
            lon: longitude local
            lat: latitude local
            self.r
        Returns:
            self.lon_r
            self.lat_r
        """

        # lat_r
        self.lat_r = radian2angle(self.r / R_EARTH)

        # lon_r
        r_prime = R_EARTH * math.cos(angle2radian(lat))
        self.lon_r = radian2angle(self.r / r_prime)

    def _point_edge_dist(self, lon, lat, edge):
        lat_origin = angle2radian(self.rd_nwk.nodes[edge[0]]['lat'])
        lon_origin = angle2radian(self.rd_nwk.nodes[edge[0]]['lon'])
        lat_dest = angle2radian(self.rd_nwk.nodes[edge[1]]['lat'])
        lon_dest = angle2radian(self.rd_nwk.nodes[edge[1]]['lon'])

        a = dist(angle2radian(lat), angle2radian(lon), lat_origin, lon_origin)
        b = dist(angle2radian(lat), angle2radian(lon), lat_dest, lon_dest)
        c = dist(lat_origin, lon_origin, lat_dest, lon_dest)

        # if origin point is the closest
        if b ** 2 > a ** 2 + c ** 2:
            return a, edge[0]  # distance, point

        # if destination point is the closest
        elif a ** 2 > b ** 2 + c ** 2:
            return b, edge[1]

        if c == 0:
            return a, edge[0]
        # otherwise, calculate the Vertical length
        p = (a + b + c) / 2
        s = math.sqrt(p * math.fabs(p - a) * math.fabs(p - b) * math.fabs(p - c))
        return 2 * s / c, None

    def _get_candidates(self):
        """
        get candidates of each GPS sample with given road network
        Returns:
            self.candidates: a list of list.
                In each list are tuples (edge, distance, node)
        """

        # get trajectory without time
        traj_lon_lat = self.trajectory[:, 1:3]
        assert traj_lon_lat.shape[1] == 2

        # for every GPS sample
        for i in range(traj_lon_lat.shape[0]):

            candidate_i = set()
            lon, lat = traj_lon_lat[i, :]

            # for every edge
            for j in self.rd_nwk.edges:
                origin, dest = j[:2]
                lat_origin = self.rd_nwk.nodes[origin]['lat']
                lon_origin = self.rd_nwk.nodes[origin]['lon']
                lat_dest = self.rd_nwk.nodes[dest]['lat']
                lon_dest = self.rd_nwk.nodes[dest]['lon']
                if lat - self.lat_r <= lat_origin <= lat + self.lat_r \
                        and lon - self.lon_r <= lon_origin <= lon + self.lon_r \
                        or lat - self.lat_r <= lat_dest <= lat + self.lat_r \
                        and lon - self.lon_r <= lon_dest <= lon + self.lon_r:
                    candidate_i.add((origin, dest))
                elif lat - self.lat_r <= lat_origin / 2 + lat_dest / 2 <= lat + self.lat_r \
                        and lon - self.lon_r <= lon_origin / 2 + lon_dest / 2 <= lon + self.lon_r:
                    candidate_i.add((origin, dest))
            candidate_i_m = list()  # (edge, distance, point)
            for edge in candidate_i:
                distance, node = self._point_edge_dist(lon, lat, edge)
                candidate_i_m.append((edge, distance, node))
            candidate_i_m.sort(key=lambda a: a[1])  # asc
            candidate_i_m = candidate_i_m[:min(self.k, len(candidate_i_m))]
            candidate_i_k = dict()
            for edge, distance, node in candidate_i_m:
                candidate_i_k[edge] = {'distance': distance, 'node': node, "voted": 0, "pre_set": []}
            self.candidates.append(candidate_i_k)

    def _observation_probability(self):
        """

        Returns:

        """

        # for candidates of every node
        for candidate_i in self.candidates:
            for edge, dct in candidate_i.items():
                candidate_i[edge]['N'] = (1 / math.sqrt(2 * math.pi) / self.sigma * math.exp(
                    - (dct['distance'] - self.mu) ** 2 / (2 * self.sigma ** 2)))

    def _transmission_probability(self):
        """

        Returns:

        """
        i = 1
        while i < len(self.candidates):
            # j and k
            j = i - 1
            if len(self.candidates[i]) == 0:
                k = i + 1
                while len(self.candidates[k]) == 0 and k < len(self.candidates):
                    k += 1
                if k == len(self.candidates):
                    break
            else:
                k = i
            d = dist(
                angle2radian(self.trajectory[j][2]),
                angle2radian(self.trajectory[j][1]),
                angle2radian(self.trajectory[k][2]),
                angle2radian(self.trajectory[k][1])
            )
            for edge_j, dct_j in self.candidates[j].items():
                for edge_k, dct_k in self.candidates[k].items():
                    brng_jk = init_bearing(
                        angle2radian(self.trajectory[j][2]),
                        angle2radian(self.trajectory[j][1]),
                        angle2radian(self.trajectory[k][2]),
                        angle2radian(self.trajectory[k][1])
                    )
                    brng_edge_j = init_bearing(
                        angle2radian(self.rd_nwk.nodes[edge_j[0]]['lat']),
                        angle2radian(self.rd_nwk.nodes[edge_j[0]]['lon']),
                        angle2radian(self.rd_nwk.nodes[edge_j[1]]['lat']),
                        angle2radian(self.rd_nwk.nodes[edge_j[1]]['lon']),
                    )
                    try:
                        if dct_j['node'] is not None and dct_k['node'] is not None:
                            result = d / nx.astar_path_length(self.rd_nwk, dct_j['node'], dct_k['node'],
                                                              weight='distance')
                        elif dct_j['node'] is not None:
                            nd2_origin = edge_k[0]
                            lon, lat = self.rd_nwk.nodes[nd2_origin]['lon'], self.rd_nwk.nodes[nd2_origin]['lat']
                            path_len = nx.astar_path_length(self.rd_nwk, dct_j['node'], nd2_origin, weight='distance')
                            path_len += math.sqrt(
                                math.fabs(
                                    dist(
                                        angle2radian(self.trajectory[k][2]),
                                        angle2radian(self.trajectory[k][1]),
                                        angle2radian(lat),
                                        angle2radian(lon)
                                    ) ** 2 - dct_k['distance'] ** 2
                                )
                            )
                            if edge_j[1] == dct_j['edge']:
                                path_len += self.rd_nwk[edge_j[0]][edge_j[1]]['distance'] * 2
                            result = d / path_len

                        elif dct_k['node'] is not None:
                            nd1_destination = edge_j[1]
                            lon, lat = self.rd_nwk.nodes[nd1_destination]['lon'], self.rd_nwk.nodes[nd1_destination][
                                'lat']
                            path_len = nx.astar_path_length(self.rd_nwk, nd1_destination, dct_k['node'],
                                                            weight='distance')
                            path_len += math.sqrt(
                                math.fabs(
                                    dist(
                                        angle2radian(self.trajectory[j][2]),
                                        angle2radian(self.trajectory[j][1]),
                                        angle2radian(lat),
                                        angle2radian(lon)
                                    ) ** 2 - dct_j['distance'] ** 2
                                )
                            )
                            if edge_k[1] == dct_k['node']:
                                path_len += self.rd_nwk[edge_k[0]][edge_k[1]]['distance'] * 2
                            result = d / path_len
                        else:
                            if edge_j == edge_k and math.fabs(brng_edge_j - brng_jk) < 90:
                                result = 1
                            else:
                                nd1_destination = edge_j[1]
                                lon1, lat1 = self.rd_nwk.nodes[nd1_destination]['lon'], \
                                    self.rd_nwk.nodes[nd1_destination]['lat']
                                nd2_origin = edge_k[0]
                                lon2, lat2 = self.rd_nwk.nodes[nd2_origin]['lon'], self.rd_nwk.nodes[nd2_origin]['lat']
                                result = d / (
                                        nx.astar_path_length(self.rd_nwk, nd1_destination, nd2_origin,
                                                             weight='distance')
                                        + math.sqrt(
                                            math.fabs(
                                                dist(
                                                    angle2radian(self.trajectory[j][2]),
                                                    angle2radian(self.trajectory[j][1]),
                                                    angle2radian(lat1),
                                                    angle2radian(lon1)
                                                ) ** 2 - dct_j['distance'] ** 2
                                            )
                                        )
                                        + math.sqrt(
                                            math.fabs(
                                                dist(
                                                    angle2radian(self.trajectory[k][2]),
                                                    angle2radian(self.trajectory[k][1]),
                                                    angle2radian(lat2),
                                                    angle2radian(lon2)
                                                ) ** 2 - dct_k['distance'] ** 2
                                            )
                                        )
                                )
                        if 'V' in dct_j.keys():
                            dct_j['V'][edge_k] = min(result, 1)
                        else:
                            dct_j['V'] = {edge_k: min(result, 1)}
                    except:
                        if 'V' in dct_j.keys():
                            dct_j['V'][edge_k] = 0
                        else:
                            dct_j['V'] = {edge_k: 0}
            i += 1

    def _temporal_analysis(self):
        """

        Returns:

        """
        # TODO

    def _score_matrix(self):
        sub_static_matrices = list()
        # for every GPS sample
        for i in range(len(self.candidates)):
            # current candidates: self.candidates[i]
            # prev candidates: self.candidates[j]
            # no current candidates
            if i == 0:
                continue
            if len(self.candidates[i]) == 0:
                sub_static_matrix = np.zeros((1, 1))
                sub_static_matrices.append(sub_static_matrix)
                continue
            # if there are current candidates, find prev index j
            j = i - 1
            while j >= 0 and len(self.candidates[j]) == 0:
                j -= 1
            # j >= 0, calculate score of candidates of GPS sample i
            if j < 0:
                sub_static_matrix = np.zeros((1, 1))
                sub_static_matrices.append(sub_static_matrix)
                continue
            sub_static_matrix = np.zeros((len(self.candidates[j].items()), len(self.candidates[i].items())))
            n = 0
            for edge, dct in self.candidates[i].items():
                m = 0
                for edge_pre, dct_pre in self.candidates[j].items():
                    sub_static_matrix[m][n] = dct['N'] * dct_pre['V'][edge] * (
                        1 if 'T' not in dct_pre.keys() else dct_pre['T'][edge])
                    m += 1
                n += 1
            sub_static_matrices.append(sub_static_matrix)
        traj_lon_lat = self.trajectory[:, 1:3]
        self.traj_points = []
        for i in range(len(traj_lon_lat)):
            W = []
            j = 0
            while j < len(traj_lon_lat):
                if i == j:
                    j += 1
                    continue
                lon_i, lat_i = traj_lon_lat[i, :]
                lon_j, lat_j = traj_lon_lat[j, :]
                euclid_distance = dist(angle2radian(lat_i), angle2radian(lon_i),
                                       angle2radian(lat_j), angle2radian(lon_j))
                W.append(pow(math.e, -(euclid_distance ** 2 / self.beta ** 2)))
                j += 1
            fai = []
            self.sub_static_matrices = sub_static_matrices
            self.W = W
            for k in range(len(W)):
                fai.append(sub_static_matrices[k] * W[k])
            traj_point = {"time": self.trajectory[i][0], "lon": self.trajectory[i][1],
                          "lat": self.trajectory[i][2], "fai": fai, "candidates": self.candidates[i]}
            self.traj_points.append(traj_point)  # Φ(fai) is the weighted score matrix

    def _interactive_voting(self):
        for traj_point in self.traj_points:
            fai = traj_point["fai"]
            for candidate in traj_point["candidates"].values():
                self._find_sequence(fai, candidate)

    def _find_sequence(self, fai, candidate):
        for i in range(len(self.candidates)):
            if candidate not in self.candidates[i].values():
                i += 1
            else:
                break
        current_p = i
        j = 0
        for c in self.candidates[i].values():
            if candidate == c:
                current_c = j
                break
            else:
                j += 1
        # get the location of current traj_point
        i += 1
        if i == len(self.candidates):
            # traj_point is in the last column
            last_point = None
            last_score = 0
        while i < len(self.candidates):
            if len(self.candidates[i]) == 0:
                i += 1
                if i == len(self.candidates):
                    last_point = None
                    last_score = 0
                    continue
            # ensure i has candidates
            j = i - 1
            while j > current_p and len(self.candidates[j]) == 0:
                j -= 1
            # ensure j has candidates
            k = 0
            for edge, dct in self.candidates[i].items():
                max_score = -float("inf")
                if j == current_p:
                    tmp = fai[i - 1][current_c][k]
                    if tmp > max_score:
                        dct["score"] = tmp
                else:
                    m = 0
                    for edge_pre, dct_pre in self.candidates[j].items():
                        tmp = dct_pre['score'] + fai[i - 1][m][k]
                        if tmp > max_score:
                            max_score = tmp
                            pre = dct_pre
                        m += 1
                    dct["score"] = max_score
                    for c in pre["pre_set"]:
                        dct["pre_set"].append(c)
                    dct["pre_set"].append(pre)
                k += 1
            i += 1
            if i == len(self.candidates):
                last_point = dct
                last_score = dct["score"]
        i = current_p - 1
        if i == -1:
            first_point = None
            first_score = 0
        while i >= 0:
            if len(self.candidates[i]) == 0:
                i -= 1
                if i == -1:
                    first_point = dct
                    first_score = dct["score"]
                continue
            j = i + 1
            while j < current_p and len(self.candidates[j]) == 0:
                j += 1
            k = 0
            for edge, dct in self.candidates[i].items():
                max_score = -float("inf")
                if j == current_p:
                    tmp = fai[j - 1][k][current_c]
                    if tmp > max_score:
                        dct["score"] = tmp
                else:
                    m = 0
                    for edge_pre, dct_pre in self.candidates[j].items():
                        tmp = dct_pre['score'] + fai[j - 1][k][m]
                        if tmp > max_score:
                            max_score = tmp
                            pre = dct_pre
                        m += 1
                    dct["score"] = max_score
                    for c in pre["pre_set"]:
                        dct["pre_set"].append(c)
                    dct["pre_set"].append(pre)
                k += 1
            i -= 1
            if i == -1:
                first_point = dct
                first_score = dct["score"]
        candidate["fValue"] = first_score + last_score
        if first_point is not None:
            for point in first_point["pre_set"]:
                point["voted"] += 1
        if last_point is not None:
            for point in last_point["pre_set"]:
                point["voted"] += 1
        candidate["voted"] += 1
        for traj_point in self.traj_points:
            for c in traj_point["candidates"].values():
                c["pre_set"] = []

    def _find_matched_sequence(self):
        res = []
        for traj_point in self.traj_points:
            if len(traj_point["candidates"]) != 0:
                max_voted = 0
                fValue = 0
                for key in traj_point["candidates"].keys():
                    candidate = traj_point["candidates"][key]
                    tmp = candidate["voted"]
                    if tmp > max_voted:
                        max_voted = tmp
                        fValue = candidate["fValue"]
                        max_voted_key = key
                    elif tmp == max_voted:
                        if candidate["fValue"] > fValue:
                            max_voted = tmp
                            fValue = candidate["fValue"]
                            max_voted_key = key
            else:
                max_voted_key = None
            res.append(max_voted_key)

        # to geo_id
        res_lst_rel = np.array(list(map(lambda x: self.rd_nwk.edges[x]['geo_id'] if x is not None else None, res)))
        dyna_id_lst = self.trajectory[:, 0].astype(int)
        if self.with_time:
            time_lst = self.trajectory[:, 3]
            res_all = np.stack([dyna_id_lst, res_lst_rel, time_lst], axis=1)
        else:
            res_all = np.stack([dyna_id_lst, res_lst_rel], axis=1)

        # set self.res_dct
        if self.usr_id in self.res_dct.keys():
            self.res_dct[self.usr_id][self.traj_id] = res_all

        else:
            self.res_dct[self.usr_id] = {self.traj_id: res_all}
