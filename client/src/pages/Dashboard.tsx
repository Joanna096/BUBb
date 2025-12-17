import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Layout } from '@/components/Layout';
import { useVolunteers } from '@/context/VolunteerContext';
import { Users, UserCheck, TrendingUp, Clock } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { cn } from '@/lib/utils';

export default function Dashboard() {
  const { volunteers } = useVolunteers();
  
  const totalVolunteers = volunteers.length;
  const avgTrust = totalVolunteers > 0 
    ? (volunteers.reduce((acc, curr) => acc + curr.trustMetrics.punctuality, 0) / totalVolunteers).toFixed(1)
    : "0";
  const totalReviews = volunteers.reduce((acc, curr) => acc + curr.trustMetrics.reviews, 0);

  // Skill Distribution Data
  const skillCounts: Record<string, number> = {};
  volunteers.forEach(v => {
    v.skills.forEach(s => {
      skillCounts[s.type] = (skillCounts[s.type] || 0) + 1;
    });
  });
  const skillData = Object.entries(skillCounts).map(([name, value]) => ({ name, value }));
  const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e'];

  // Availability Distribution
  const availabilityCounts: Record<string, number> = { '平日': 0, '週末': 0 };
  volunteers.forEach(v => {
    v.availability.forEach(a => {
      if (a.includes('平日')) availabilityCounts['平日']++;
      if (a.includes('週末')) availabilityCounts['週末']++;
    });
  });
  const availabilityData = Object.entries(availabilityCounts).map(([name, value]) => ({ name, value }));

  return (
    <Layout>
      <div className="space-y-8 animate-in fade-in duration-500">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">經營儀表板</h1>
          <p className="text-slate-500 mt-1">即時掌握志工池健康度與人力分佈</p>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard 
            title="總志工人數" 
            value={totalVolunteers} 
            icon={Users} 
            trend="+2% 本月"
            color="text-indigo-600"
            bg="bg-indigo-50"
          />
          <StatCard 
            title="平均準時率" 
            value={`${avgTrust}%`} 
            icon={Clock} 
            trend="維持高標"
            color="text-emerald-600"
            bg="bg-emerald-50"
          />
          <StatCard 
            title="活躍參與者" 
            value={Math.floor(totalVolunteers * 0.8)} 
            icon={UserCheck} 
            trend="80% 活躍率"
            color="text-blue-600"
            bg="bg-blue-50"
          />
          <StatCard 
            title="總評價數" 
            value={totalReviews} 
            icon={TrendingUp} 
            trend="+5 新增"
            color="text-purple-600"
            bg="bg-purple-50"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="shadow-sm border-slate-200">
            <CardHeader>
              <CardTitle>能力分佈概況</CardTitle>
              <CardDescription>各類專長志工的人數統計</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={skillData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" width={80} tick={{fill: '#64748b'}} axisLine={false} />
                    <Tooltip cursor={{fill: '#f1f5f9'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                    <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]} barSize={32} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-sm border-slate-200">
            <CardHeader>
              <CardTitle>時段偏好分析</CardTitle>
              <CardDescription>平日與週末的人力資源對比</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] w-full flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={availabilityData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      fill="#8884d8"
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {availabilityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? '#3b82f6' : '#8b5cf6'} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-center gap-6 text-sm text-slate-600 mt-[-20px]">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                  平日時段
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-violet-500"></div>
                  週末時段
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
}

function StatCard({ title, value, icon: Icon, trend, color, bg }: any) {
  return (
    <Card className="border-none shadow-sm hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-center justify-between space-y-0 pb-2">
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <div className={cn("p-2 rounded-full", bg)}>
            <Icon className={cn("h-4 w-4", color)} />
          </div>
        </div>
        <div className="flex items-end justify-between mt-2">
          <div className="text-2xl font-bold text-slate-900">{value}</div>
          <p className={cn("text-xs font-medium bg-slate-100 px-2 py-0.5 rounded-full text-slate-600")}>
            {trend}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
