#! /usr/bin/env python

# Reference: https://libvirt.org/html/libvirt-libvirt-domain.html
#
# Author: Md Safiyat Reza <md.reza@snapdeal.com>

import libvirt
import os
import sys
import time
from xml.etree import ElementTree as etree

# nagios exit code
STATUS_OK = 0
STATUS_WARNING = 1
STATUS_ERROR = 2
STATUS_UNKNOWN = 3

domainstate = {}
domainstate['0'] = 'NOSTATE'
domainstate['1'] = 'RUNNING'
domainstate['2'] = 'BLOCKED'
domainstate['3'] = 'PAUSED'
domainstate['4'] = 'SHUTDOWN'
domainstate['5'] = 'SHUTOFF'
domainstate['6'] = 'CRASHED'
domainstate['7'] = 'PMSUSPENDED'
domainstate['8'] = 'LAST'
domainstate['NOSTATE'] = {}
domainstate['RUNNING'] = {}
domainstate['BLOCKED'] = {}
domainstate['PAUSED'] = {}
domainstate['SHUTDOWN'] = {}
domainstate['SHUTOFF'] = {}
domainstate['CRASHED'] = {}
domainstate['PMSUSPENDED'] = {}
domainstate['LAST'] = {}
domainstate['NOSTATE']['0'] = 'UNKNOWN'
domainstate['NOSTATE']['1'] = 'LAST'
domainstate['RUNNING']['0'] = 'UNKNOWN'
domainstate['RUNNING']['1'] = 'BOOTED'
domainstate['RUNNING']['2'] = 'MIGRATED'
domainstate['RUNNING']['3'] = 'RESTORED'
domainstate['RUNNING']['4'] = 'FROM_SNAPSHOT'
domainstate['RUNNING']['5'] = 'UNPAUSED'
domainstate['RUNNING']['6'] = 'MIGRATION_CANCELLED'
domainstate['RUNNING']['7'] = 'SAVE_CANCELLED'
domainstate['RUNNING']['8'] = 'WAKEUP'
domainstate['RUNNING']['9'] = 'CRASHED'
domainstate['RUNNING']['10'] = 'LAST'
domainstate['BLOCKED']['0'] = 'UNKNOWN'
domainstate['BLOCKED']['1'] = 'LAST'
domainstate['PAUSED']['0'] = 'UNKNOWN'
domainstate['PAUSED']['1'] = 'USER'
domainstate['PAUSED']['2'] = 'MIGRATION'
domainstate['PAUSED']['3'] = 'SAVE'
domainstate['PAUSED']['4'] = 'DUMP'
domainstate['PAUSED']['5'] = 'IOERROR'
domainstate['PAUSED']['6'] = 'WATCHDOG'
domainstate['PAUSED']['7'] = 'FROM_SNAPSHOT'
domainstate['PAUSED']['8'] = 'SHUTTING_DOWN'
domainstate['PAUSED']['9'] = 'SNAPSHOT'
domainstate['PAUSED']['10'] = 'CRASHED'
domainstate['PAUSED']['11'] = 'STARTING_UP'
domainstate['PAUSED']['12'] = 'LAST'
domainstate['SHUTDOWN']['0'] = 'UNKNOWN'
domainstate['SHUTDOWN']['1'] = 'USER'
domainstate['SHUTDOWN']['2'] = 'LAST'
domainstate['SHUTOFF']['0'] = 'UNKNOWN'
domainstate['SHUTOFF']['1'] = 'SHUTDOWN'
domainstate['SHUTOFF']['2'] = 'DESTROYED'
domainstate['SHUTOFF']['3'] = 'CRASHED'
domainstate['SHUTOFF']['4'] = 'MIGRATED'
domainstate['SHUTOFF']['5'] = 'SAVED'
domainstate['SHUTOFF']['6'] = 'FAILED'
domainstate['SHUTOFF']['7'] = 'FROM_SNAPSHOT'
domainstate['SHUTOFF']['8'] = 'LAST'
domainstate['CRASHED']['0'] = 'UNKNOWN'
domainstate['CRASHED']['1'] = 'PANICKED'
domainstate['CRASHED']['2'] = 'LAST'
domainstate['PMSUSPENDED']['0'] = 'UNKNOWN'
domainstate['PMSUSPENDED']['1'] = 'LAST'

def read_cpu_time(instance_uuid):
    fp = open('/tmp/%s-cpu' % instance_uuid, 'r')
    t, cpuTime = fp.read().split()
    t = float(t)
    cpuTime = float(cpuTime)
    fp.close()
    return t, cpuTime

def write_cpu_time(instance_uuid, cpu_time, t):
    fp = open('/tmp/%s-cpu' % instance_uuid, 'w')
    fp.write('%s %s' % (t, cpu_time))
    fp.close()

def calc_cpu_perc(instance_uuid, cpu_time, t):
    curT = t
    curCpuTime = cpu_time
    if not os.path.isfile('/tmp/%s-cpu' % instance_uuid):
        write_cpu_time(instance_uuid, curCpuTime, curT)
        return 0.0
    prevT, prevCpuTime = read_cpu_time(instance_uuid)
    write_cpu_time(instance_uuid, curCpuTime, curT)
    return (curCpuTime - prevCpuTime) / ((curT - prevT) * 10000000)

def read_block_stats(instance_uuid, disk):
    fp = open('/tmp/%s-block-%s' % (instance_uuid, disk), 'r')
    t, readB, readR, writeB, writeR = fp.read().split()
    t = float(t)
    readB = int(readB)
    readR = int(readR)
    writeB = int(writeB)
    writeR = int(writeR)
    fp.close()
    return t, readB, readR, writeB, writeR

def write_block_stats(instance_uuid, disk, t, stats):
    fp = open('/tmp/%s-block-%s' % (instance_uuid, disk), 'w')
    fp.write('%s %s %s %s %s' % (t, stats[1], stats[0], stats[3], stats[2]))
    fp.close()

def calc_block_stats(instance_uuid, disk, t, stats):
    if not os.path.isfile('/tmp/%s-block-%s' % (instance_uuid, disk)):
        write_block_stats(instance_uuid, disk, t, stats)
        return 0.0
    prevT, prevReadB, prevReadR, prevWriteB, prevWriteR = read_block_stats(
        instance_uuid, disk)
    write_block_stats(instance_uuid, disk, t, stats)
    diff = [cur - prev for cur, prev in zip([t, stats[1], stats[0], stats[3],
                                             stats[2]], [prevT, prevReadB,
                                                         prevReadR, prevWriteB,
                                                         prevWriteR])]
    change = {}
    change['time'] = diff[0]
    change['read_bytes'] = diff[1]
    change['read_ops'] = diff[2]
    change['write_bytes'] = diff[3]
    change['write_ops'] = diff[4]
    return change

def read_interface_stats(instance_uuid, interface):
    fp = open('/tmp/%s-interface-%s' % (instance_uuid, interface), 'r')
    t, rx_bytes, rx_packets, rx_errs, rx_drop, tx_bytes, tx_packets, tx_errs, tx_drop = fp.read().split()
    t = float(t)
    rx_bytes = int(rx_bytes)
    rx_packets = int(rx_packets)
    rx_errs = int(rx_errs)
    rx_drop = int(rx_drop)
    tx_bytes = int(tx_bytes)
    tx_packets = int(tx_packets)
    tx_errs = int(tx_errs)
    tx_drop = int(tx_drop)
    fp.close()
    return t, rx_bytes, rx_packets, rx_errs, rx_drop, tx_bytes, tx_packets, tx_errs, tx_drop

def write_interface_stats(instance_uuid, interface, t, stats):
    fp = open('/tmp/%s-interface-%s' % (instance_uuid, interface), 'w')
    fp.write('%s %s %s %s %s %s %s %s %s' % (t, stats[0], stats[1], stats[2],
                                          stats[3], stats[4], stats[5],
                                          stats[6], stats[7]))
    fp.close()

def calc_interface_stats(instance_uuid, interface, t, stats):
    if not os.path.isfile('/tmp/%s-interface-%s' % (instance_uuid, interface)):
        write_interface_stats(instance_uuid, interface, t, stats)
        return 0.0
    prevT, prevRx_bytes, prevRx_packets, prevRx_errs, prevRx_drop, prevTx_bytes, prevTx_packets, prevTx_errs, prevTx_drop = read_interface_stats(instance_uuid, interface)
    write_interface_stats(instance_uuid, interface, t, stats)
    diff = [cur - prev for cur, prev in zip([t, stats[0], stats[1], stats[2],
                                             stats[3], stats[4], stats[5],
                                             stats[6], stats[7]],
                                            [prevT, prevRx_bytes,
                                             prevRx_packets, prevRx_errs,
                                             prevRx_drop, prevTx_bytes,
                                             prevTx_packets, prevTx_errs,
                                             prevTx_drop])]
    change = {}
    change['time'] = diff[0]
    change['rx_bytes'] = diff[1]
    change['rx_packets'] = diff[2]
    change['rx_errs'] = diff[3]
    change['rx_drop'] = diff[4]
    change['tx_bytes'] = diff[5]
    change['tx_packets'] = diff[6]
    change['tx_errs'] = diff[7]
    change['tx_drop'] = diff[8]
    return change


def get_stats():
    conn = libvirt.openReadOnly('qemu:///system')
    namespaces = {'nova':'http://openstack.org/xmlns/libvirt/nova/1.0'}

    stats_all = {}

    for instance in conn.listAllDomains():
        inst = {}
        xml_data = etree.fromstring(instance.XMLDesc())
        uuid = xml_data.find('uuid').text

        inst['uuid'] = uuid
        inst['name'] = xml_data.find('metadata/nova:instance/nova:name',
                             namespaces=namespaces).text
        inst['flavor'] = xml_data.find('metadata/nova:instance/nova:flavor',
                               namespaces=namespaces).attrib['name']
        inst['memory'] = xml_data.find('metadata/nova:instance/nova:flavor/nova:memory',
                               namespaces=namespaces).text
        inst['disk'] = xml_data.find('metadata/nova:instance/nova:flavor/nova:disk',
                             namespaces=namespaces).text
        inst['swap'] = xml_data.find('metadata/nova:instance/nova:flavor/nova:swap',
                             namespaces=namespaces).text
        inst['ephemeral'] = xml_data.find(
            'metadata/nova:instance/nova:flavor/nova:ephemeral',
            namespaces=namespaces).text
        inst['vcpus'] = xml_data.find('metadata/nova:instance/nova:flavor/nova:vcpus',
                              namespaces=namespaces).text
        inst['owner'] = xml_data.find('metadata/nova:instance/nova:owner/nova:user',
                              namespaces=namespaces).text
        inst['project'] = xml_data.find('metadata/nova:instance/nova:owner/nova:project',
                                namespaces=namespaces).text

        state, reason = instance.state()
        inst['state'] = state
        inst['reason'] = reason
        if state != 1:
            stats_all[uuid] = inst
            continue

        cpu_perc = calc_cpu_perc(uuid, instance.getCPUStats(1)[0]['cpu_time'],
                                 time.time()) / int(inst['vcpus'])
        inst['cpu_stats'] = cpu_perc

        inst_mem = instance.memoryStats()
        stats = {}
        if 'available' in inst_mem:
            stats['total'] = int(inst_mem['available'])
            stats['free'] = int(inst_mem['unused'])
        else:
            stats['total'] = -1
            stats['free'] = -1
        stats['used'] = stats['total'] - stats['free']
        stats['percentage'] = stats['used'] * 100.0 / stats['total']
        inst['memory_stats'] = stats

        stats = {}
        for disk in xml_data.findall('devices/disk', namespaces=namespaces):
            device = disk.find('target').attrib['dev']
            stats[device] = calc_block_stats(uuid, device, time.time(),
                                     instance.blockStats(device))
        inst['disk_stats'] = stats

        stats = {}
        for interface in xml_data.findall('devices/interface', namespaces=namespaces):
            device = interface.find('target').attrib['dev']
            stats[device] = calc_interface_stats(instance.UUIDString(), device, time.time(),
                                         instance.interfaceStats(device))
        inst['interface_stats'] = stats

        stats_all[uuid] = inst


    instance_count = len(stats_all)
    instance_running_count = 0
    firstLine = 'Number of Instances: %d' % instance_count
    output = ''
    graphite = ''
    return stats_all
    """ 
    for uuid, instance in stats_all.items():
        output += '\n%s (%s, %s, %s)\n' % (instance['uuid'], instance['name'],
                                         instance['owner'], instance['project'])
        output += '\tState: %s    Reason: %s\n' % (domainstate[str(instance['state'])],
                                                  domainstate[domainstate[str(instance['state'])]][str(instance['reason'])])
        if instance['state'] != 1:
            continue
        instance_running_count += 1
        output += '\tCPU: %.2f %%    VCPUs: %s\n' % (instance['cpu_stats'], instance['vcpus'])
        graphite += 'CPU in %% - %s=%.2f;90;95;0;100 ' % (instance['name'], instance['cpu_stats'])

        output += '\tMemory: %.2f %% (%.2f GB of %.0f GB)\n' % (instance['memory_stats'][
            'percentage'], instance['memory_stats']['used'] / 1048576.0, instance[
                'memory_stats']['total'] / 1048576.0)
        graphite += 'Memory in %% - %s=%.2f;90;95;0;100 ' % (instance['name'], instance['memory_stats']['percentage'])

        output += '\tDISK:\n'
        iops_cons = 0
        for disk_name, disk in instance['disk_stats'].items():
            iops = (disk['read_ops'] + disk['write_ops']) / (disk['time'])
            iops_cons += iops
            output += '\t  %s: %.2f IOPS, %.2f kB/s (read), %.2f kB/s (write)\n' % (
                disk_name, (disk['read_ops'] + disk['write_ops']) / (disk['time']),
                disk['read_bytes'] / (1024.0 * disk['time']), disk['write_bytes'] / (
                    1024.0 * disk['time']))
        graphite += 'Disk in IOPS - %s=%.2f;;;; ' % (instance['name'], iops_cons)

        output += '\tINTERFACE:\n'
        kbps_cons = 0
        for interface_name, interface in instance['interface_stats'].items():
            kbps = (interface['rx_bytes'] + interface['tx_bytes']) / (interface['time'] * 1024.0)
            kbps_cons += kbps
            output += '\t  %s: %.2f kB/s, %.2f pkts/s (read), %.2f pkts/s (write)\n' % (
                interface_name, kbps, interface['rx_packets'] / interface['time'],
                interface['tx_packets'] / interface['time'])
        graphite += 'Interface in kBps - %s=%.2f;;;; ' % (instance['name'], kbps_cons)

    print firstLine + ' | ' + graphite + output

    if instance_running_count == instance_count:
        return STATUS_OK
    if instance_running_count == 0:
        return STATUS_ERROR
    if instance_running_count < instance_count:
        return STATUS_WARNING
    """
#if __name__ == '__main__':
#    sys.exit(main())

