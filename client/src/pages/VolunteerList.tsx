import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, Filter, Phone, MessageCircle, Star, Calendar, Plus, ChevronRight, CheckCircle2 } from 'lucide-react';
import { MOCK_VOLUNTEERS, SKILL_OPTIONS, TIME_OPTIONS, type Volunteer, type SkillType, type Availability } from '@/lib/data';
import { Layout } from '@/components/Layout';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

export default function VolunteerList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSkills, setSelectedSkills] = useState<SkillType[]>([]);
  const [selectedTime, setSelectedTime] = useState<Availability | 'ALL'>('ALL');
  const [volunteers, setVolunteers] = useState(MOCK_VOLUNTEERS);
  const { toast } = useToast();

  // Filter Logic
  const filteredVolunteers = volunteers.filter(v => {
    const matchesSearch = v.name.includes(searchTerm) || v.phone.includes(searchTerm);
    const matchesTime = selectedTime === 'ALL' || v.availability.includes(selectedTime);
    const matchesSkills = selectedSkills.length === 0 || selectedSkills.every(skill => 
      v.skills.some(s => s.type === skill && s.level >= 3) // Assume level 3+ is "competent"
    );
    return matchesSearch && matchesTime && matchesSkills;
  });

  const toggleSkill = (skill: SkillType) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter(s => s !== skill));
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const handleAddRecord = (volunteerId: string, event: string, role: string) => {
    setVolunteers(prev => prev.map(v => {
      if (v.id === volunteerId) {
        return {
          ...v,
          history: [...v.history, { 
            id: Math.random().toString(), 
            eventName: event, 
            role: role, 
            date: new Date().toISOString().split('T')[0] 
          }],
          trustMetrics: {
            ...v.trustMetrics,
            reviews: v.trustMetrics.reviews + 1
          }
        };
      }
      return v;
    }));
    toast({
      title: "紀錄已新增",
      description: "成功新增一筆活動參與紀錄",
    });
  };

  return (
    <Layout>
      <div className="space-y-6 animate-in fade-in duration-500">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">志工搜尋器</h1>
            <p className="text-slate-500 mt-1">根據能力與時間篩選適合的人選</p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="px-3 py-1 bg-white">
              總計: {filteredVolunteers.length} 人
            </Badge>
          </div>
        </div>

        {/* Search & Filters */}
        <Card className="border-none shadow-sm bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6 space-y-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input 
                  placeholder="搜尋姓名或電話..." 
                  className="pl-9 border-slate-200 focus:ring-indigo-500" 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select value={selectedTime} onValueChange={(val: any) => setSelectedTime(val)}>
                <SelectTrigger className="w-[180px] border-slate-200">
                  <SelectValue placeholder="選擇服務時段" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ALL">所有時段</SelectItem>
                  {TIME_OPTIONS.map(t => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-wrap gap-2 items-center">
              <span className="text-sm font-medium text-slate-600 mr-2 flex items-center gap-1">
                <Filter className="w-4 h-4" />
                能力篩選:
              </span>
              {SKILL_OPTIONS.map(skill => (
                <Badge 
                  key={skill}
                  variant={selectedSkills.includes(skill) ? "default" : "outline"}
                  className={cn(
                    "cursor-pointer transition-all hover:scale-105",
                    selectedSkills.includes(skill) 
                      ? "bg-indigo-600 hover:bg-indigo-700 border-indigo-600" 
                      : "hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200 bg-white"
                  )}
                  onClick={() => toggleSkill(skill)}
                >
                  {skill}
                </Badge>
              ))}
              {selectedSkills.length > 0 && (
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setSelectedSkills([])}
                  className="text-xs text-slate-400 hover:text-slate-600"
                >
                  清除
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Results Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredVolunteers.map(volunteer => (
            <VolunteerCard 
              key={volunteer.id} 
              volunteer={volunteer} 
              onAddRecord={handleAddRecord}
            />
          ))}
          
          {filteredVolunteers.length === 0 && (
            <div className="col-span-full py-12 text-center text-slate-400">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8 opacity-50" />
              </div>
              <p>沒有找到符合條件的志工</p>
              <Button 
                variant="link" 
                onClick={() => {setSearchTerm(''); setSelectedSkills([]); setSelectedTime('ALL');}}
              >
                清除所有篩選條件
              </Button>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

function VolunteerCard({ volunteer, onAddRecord }: { volunteer: Volunteer, onAddRecord: (id: string, event: string, role: string) => void }) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newEvent, setNewEvent] = useState('');
  const [newRole, setNewRole] = useState('');

  const handleSubmit = () => {
    if (newEvent && newRole) {
      onAddRecord(volunteer.id, newEvent, newRole);
      setNewEvent('');
      setNewRole('');
      setIsDialogOpen(false);
    }
  };

  return (
    <Card className="overflow-hidden border-slate-200 shadow-sm hover:shadow-md transition-shadow group">
      <CardHeader className="pb-3 bg-slate-50/50 border-b border-slate-100">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <img 
              src={volunteer.avatar} 
              alt={volunteer.name} 
              className="w-12 h-12 rounded-full border-2 border-white shadow-sm"
            />
            <div>
              <CardTitle className="text-lg font-bold text-slate-800 flex items-center gap-2">
                {volunteer.name}
                {volunteer.trustMetrics.taskCompletion > 4.5 && (
                  <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                )}
              </CardTitle>
              <div className="flex gap-2 text-xs text-slate-500 mt-1">
                <span className="flex items-center gap-1"><Phone className="w-3 h-3" /> {volunteer.phone}</span>
                <span className="flex items-center gap-1"><MessageCircle className="w-3 h-3" /> {volunteer.lineId}</span>
              </div>
            </div>
          </div>
          <Badge variant={volunteer.trustMetrics.punctuality > 90 ? "default" : "secondary"} className={
             volunteer.trustMetrics.punctuality > 90 ? "bg-emerald-500 hover:bg-emerald-600" : ""
          }>
            {volunteer.trustMetrics.punctuality}% 準時
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="pt-4 space-y-4">
        {/* Skills */}
        <div className="space-y-2">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">能力標籤</p>
          <div className="flex flex-wrap gap-1.5">
            {volunteer.skills.map(s => (
              <Badge key={s.type} variant="secondary" className="bg-slate-100 text-slate-600 border-slate-200">
                {s.type} <span className="text-slate-400 ml-1">Lv.{s.level}</span>
              </Badge>
            ))}
          </div>
        </div>

        {/* Availability */}
        <div className="space-y-2">
           <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">可服務時段</p>
           <p className="text-sm text-slate-600">{volunteer.availability.join('、')}</p>
        </div>

        {/* Action Button */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="w-full mt-2 bg-white text-indigo-600 border border-indigo-200 hover:bg-indigo-50 hover:border-indigo-300">
              <Plus className="w-4 h-4 mr-2" /> 新增紀錄
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>新增活動紀錄 - {volunteer.name}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>活動名稱</Label>
                <Input 
                  placeholder="例如：2025 新年市集" 
                  value={newEvent} 
                  onChange={e => setNewEvent(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>擔任角色</Label>
                <Select value={newRole} onValueChange={setNewRole}>
                  <SelectTrigger>
                    <SelectValue placeholder="選擇角色" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="引導人員">引導人員</SelectItem>
                    <SelectItem value="行政協助">行政協助</SelectItem>
                    <SelectItem value="機動支援">機動支援</SelectItem>
                    <SelectItem value="攝影紀錄">攝影紀錄</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>取消</Button>
              <Button onClick={handleSubmit} disabled={!newEvent || !newRole}>確認新增</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
}
